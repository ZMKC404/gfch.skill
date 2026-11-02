#!/usr/bin/env python3
"""gfch.skill 语料 canonical 层处理：哥飞公众号(615 md) + 出海创业指南(12 拆解文)
→ index/chunks/METADATA/manifest/image 清单。

用法: python3 -I tools/process_corpus.py
输入: _staging/gefei_raw/*.md          （哥飞公众号全部.zip 解包，GBK 文件名已修复）
      _staging/chuhai_raw/<标题>/*.md  （出海创业指南 12 个 zip 解包，各含 1 md + 1 缩略图）
输出: corpus/gefei/{canonical/index.md, canonical/chunks.jsonl, 00_台账/*}
      corpus/chuhai/同上
幂等可复跑，输出目录每次重建。原始 zip 零改动（台账记录 SHA256）。
"""
from __future__ import annotations
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STAGE = REPO / "_staging"
OUT = REPO / "corpus"

# 微信导出常见噪声行（整行剔除，均不涉及正文风格）
NOISE_PATTERNS = [
    r"^预览时标签不可点$", r"^微信扫一扫.*$", r"^轻扫二维码.*$",
    r"^扫一扫关注该公众号.*$", r"^(分享|收藏|点赞|在看|阅读原文|继续阅读)$",
    r"^喜欢此内容的人还喜欢$", r"^人划线$", r"^划线$", r"^选择留言身份$",
    r"^\s*$",
]
NOISE_RE = [re.compile(p) for p in NOISE_PATTERNS]
IMG_LINE_RE = re.compile(r"^\s*!\[[^\]]*\]\(([^)]*)\)\s*$")
IMG_INLINE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
JS_LINK_RE = re.compile(r"\[([^\]]*)\]\(javascript:void\(0?\)?;?\)")
HTML_TAG_RE = re.compile(r"</?[a-zA-Z][^>]*>")
DATE_RE = re.compile(r"(20\d{2})[-/年.](\d{1,2})[-/月.]")
AUTHOR_RE = re.compile(r"原创\s*([^\s\[]+)")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clean_gefei(raw: str) -> tuple[str, str, str | None, list[str]]:
    """清洗哥飞公众号导出 md。返回 (正文, 作者, date_hint, 图片URL列表)。"""
    lines = raw.replace("\\(", "(").replace("\\)", ")").splitlines()
    author, date_hint, cover = None, None, None
    imgs: list[str] = []
    out = []
    for i, line in enumerate(lines):
        m = IMG_LINE_RE.match(line)
        if m:
            url = m.group(1)
            imgs.append(url)
            if i < 3 and "cover_image" in line:
                cover = url
            continue
        if author is None and i < 8:
            am = AUTHOR_RE.search(line)
            if am:
                author = am.group(1)
        if date_hint is None and i < 15:
            dm = DATE_RE.search(line)
            if dm:
                date_hint = f"{dm.group(1)}-{int(dm.group(2)):02d}"
        line = JS_LINK_RE.sub(r"\1", line)
        line = HTML_TAG_RE.sub("", line)
        line = line.strip()
        if any(rx.match(line) for rx in NOISE_RE):
            continue
        out.append(line)
    # 折叠连续空行
    text, blank = [], 0
    for line in out:
        if not line:
            blank += 1
            if blank > 1:
                continue
        else:
            blank = 0
        text.append(line)
    body = "\n".join(text).strip()
    # 去掉与文件名重复的标题行及下划线行
    parts = body.split("\n")
    if len(parts) >= 2 and parts[1].strip() and set(parts[1].strip()) <= {"=", " "}:
        parts = parts[2:]
    body = "\n".join(parts).strip()
    return body, (author or ""), date_hint, imgs


SPAN_RE = re.compile(r'<span style="[^"]*background-color:\s*rgba\(255,\s*246,\s*122[^"]*">(.*?)</span>', re.S)
SPAN_ANY_RE = re.compile(r"<span[^>]*>(.*?)</span>", re.S)


def clean_chuhai(raw: str) -> tuple[str, str | None, list[str]]:
    """清洗出海创业指南拆解文。返回 (正文, date_hint, 本地图片列表)。
    源文中黄色背景 span = 阅读划线高亮，转 markdown 粗体保留信号。"""
    text = raw.replace("&#x20;", "").replace("\\(", "(").replace("\\)", ")")
    text = SPAN_RE.sub(r"**\1**", text)          # 划线高亮 → 粗体
    text = SPAN_ANY_RE.sub(r"\1", text)           # 其余 span 解包
    lines = text.splitlines()
    date_hint, imgs, out = None, [], []
    for i, line in enumerate(lines):
        m = IMG_LINE_RE.match(line)
        if m:
            imgs.append(m.group(1))
            continue
        if date_hint is None and i < 15:
            dm = DATE_RE.search(line)
            if dm:
                date_hint = f"{dm.group(1)}-{int(dm.group(2)):02d}"
        line = HTML_TAG_RE.sub("", line)
        out.append(line)
    body, blank = [], 0
    for line in out:
        if not line.strip():
            blank += 1
            if blank > 1:
                continue
        else:
            blank = 0
        body.append(line.rstrip())
    return "\n".join(body).strip(), date_hint, imgs


def content_chars(text: str) -> int:
    return len(re.sub(r"\s", "", text))


def write_outputs(slug: str, name: str, records: list[dict], extra_meta: list[str]) -> dict:
    out = OUT / slug
    out.mkdir(parents=True, exist_ok=True)
    (out / "canonical").mkdir(exist_ok=True)
    (out / "00_台账").mkdir(exist_ok=True)
    with open(out / "canonical/chunks.jsonl", "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(out / "canonical/index.md", "w", encoding="utf-8") as f:
        f.write(f"# {name} · 文章索引（{len(records)} 篇）\n\n")
        f.write("> 全文见 chunks.jsonl（字段 text）；图片清单见 00_台账/image-index.csv。\n\n")
        f.write("| # | 标题 | 字数 | 图片数 | 作者 |\n|---|---|---|---|---|\n")
        for i, r in enumerate(records, 1):
            f.write(f"| {i} | {r['title'][:60]} | {r['chars']} | {len(r.get('images', []))} | {r.get('author', '-')} |\n")
    chars = sorted(r["chars"] for r in records)
    meta = [
        f"# METADATA · {name}（{slug}）",
        f"- 生成时间: {datetime.now().isoformat(timespec='seconds')}",
        f"- 有效文章: {len(records)} 篇 / 总字数 {sum(chars):,}",
        f"- 单篇字数: 中位 {chars[len(chars)//2] if chars else 0} / 最短 {chars[0] if chars else 0} / 最长 {chars[-1] if chars else 0}",
        *extra_meta,
    ]
    (out / "00_台账/METADATA.md").write_text("\n".join(meta) + "\n", encoding="utf-8")
    entries = [(out / "canonical/index.md", "canonical/index.md"),
               (out / "canonical/chunks.jsonl", "canonical/chunks.jsonl"),
               (out / "00_台账/METADATA.md", "00_台账/METADATA.md")]
    with open(out / "00_台账/manifest.sha256", "w", encoding="utf-8") as f:
        for p, label in entries:
            f.write(f"{sha256(p)}  {label}\n")
    return {"slug": slug, "articles": len(records), "total_chars": sum(chars)}


def process_gefei() -> dict:
    src = STAGE / "gefei_raw"
    records = []
    for md in sorted(src.glob("*.md")):
        raw = md.read_text(encoding="utf-8", errors="replace")
        body, author, date_hint, imgs = clean_gefei(raw)
        title = md.stem.replace("\n", " ").strip()
        if content_chars(body) < 50:
            continue
        records.append({
            "id": f"gefei-{len(records):05d}", "blogger": "我是哥飞", "slug": "gefei",
            "title": title, "date_hint": date_hint, "author": author or "我是哥飞",
            "chars": content_chars(body), "source": str(md),
            "cover": imgs[0] if imgs else None, "images": imgs, "text": body,
        })
    img_rows = ["article,image_url,seq"]
    for r in records:
        for seq, u in enumerate(r["images"]):
            img_rows.append(f"{r['id']},{u},{seq}")
    (OUT / "gefei/00_台账").mkdir(parents=True, exist_ok=True)
    (OUT / "gefei/00_台账/image-index.csv").write_text("\n".join(img_rows) + "\n", encoding="utf-8")
    guests = sorted({r["author"] for r in records} - {"我是哥飞", "哥飞"})
    meta = [
        "- 来源: 哥飞公众号全部.zip（615 个 md，微信导出）",
        "- 作者字段: 首部「原创 X」提取；非哥飞署名视为客投/转载并保留原署名",
        f"- 客投/转载署名: {', '.join(guests) if guests else '无'}",
        "- date_hint: 文内前 15 行提及的年月，仅参考不可当发布日期（多数文章无发布日期）",
        "- 清洗规则: 去封面图行/JS链接解包/HTML标签/微信页脚噪声/连续空行折叠；图片 URL 保留在 images 字段",
    ]
    s = write_outputs("gefei", "我是哥飞", records, meta)
    s["images"] = sum(len(r["images"]) for r in records)
    s["img_articles"] = sum(1 for r in records if r["images"])
    return s


def process_chuhai() -> dict:
    src = STAGE / "chuhai_raw"
    records = []
    for d in sorted(src.iterdir()):
        if not d.is_dir():
            continue
        mds = list(d.glob("*.md"))
        if not mds:
            continue
        raw = mds[0].read_text(encoding="utf-8", errors="replace")
        body, date_hint, imgs = clean_chuhai(raw)
        title = d.name.strip()
        if content_chars(body) < 50:
            continue
        records.append({
            "id": f"chuhai-{len(records):05d}", "blogger": "未署名（视频拆解体）", "slug": "chuhai",
            "title": title, "date_hint": date_hint, "author": "",
            "chars": content_chars(body), "source": str(mds[0]),
            "cover": imgs[0] if imgs else None, "images": imgs, "text": body,
        })
    meta = [
        "- 来源: 出海创业指南/ 12 个 zip，各含 1 篇视频拆解 md + 1 张 YouTube 缩略图",
        "- 作者: 源文件未署名（YouTube 视频拆解文），如实标注，不猜测",
        "- 清洗规则: 去 &#x20;/HTML 标签；黄色背景 span（阅读划线）转为 markdown 粗体保留强调信号",
        "- date_hint: 文内提及年月，仅参考",
    ]
    img_rows = ["article,image_file,seq"]
    for r in records:
        for seq, u in enumerate(r["images"]):
            img_rows.append(f"{r['id']},{u},{seq}")
    (OUT / "chuhai/00_台账").mkdir(parents=True, exist_ok=True)
    (OUT / "chuhai/00_台账/image-index.csv").write_text("\n".join(img_rows) + "\n", encoding="utf-8")
    return write_outputs("chuhai", "出海创业指南（视频拆解体）", records, meta)


def main():
    OUT.mkdir(exist_ok=True)
    s1 = process_gefei()
    print(f"[ok] gefei: {s1['articles']} 篇 / {s1['total_chars']:,} 字 / 图片 {s1['images']} 张（{s1['img_articles']} 篇有图）")
    s2 = process_chuhai()
    print(f"[ok] chuhai: {s2['articles']} 篇 / {s2['total_chars']:,} 字")

    # 原始 zip 台账
    zips = [Path("/Users/venn/Downloads/哥飞出海/哥飞公众号全部.zip"),]
    zips += sorted(Path("/Users/venn/Downloads/哥飞出海/出海创业指南").glob("*.zip"))
    zips += [Path("/Users/venn/Downloads/哥飞出海/哥飞课程/上海分享.zip")]
    lines = ["# gfch.skill 语料全局台账（canonical 层）", "",
             f"生成: {datetime.now().isoformat(timespec='seconds')}", "",
             "| slug | 来源 | 篇数 | 总字数 |", "|---|---|---|---|",
             f"| gefei | 哥飞公众号全部.zip | {s1['articles']} | {s1['total_chars']:,} |",
             f"| chuhai | 出海创业指南 12 zip | {s2['articles']} | {s2['total_chars']:,} |",
             "", "## 原始包 SHA256（零改动）"]
    for z in zips:
        if z.exists():
            lines.append(f"- {sha256(z)[:16]}…  {z.name}")
    lines += [
        "", "## 不入库记录",
        "- 哥飞课程: 上海分享.zip 8 个 Web.Cafe.ts 视频 + 2025年中分享会 mp4 + 线下分享视频与ppt.7z（百度云下载不完整）"
        " + 深圳交流会.zip（不完整）—— 视频转写成本高且核心方法与公众号语料重叠，登记后续可补层",
        "", "## 已知缺口",
        "- gefei 图片为微信 CDN 远程链接（image-index.csv 659 条），下载与视觉识别见 image-download.py 与 visual-cards 阶段",
        "- chuhai 缩略图为 YouTube maxresdefault.jpg（营销图，信息量低，仅索引）",
        "- 多数文章无发布日期，date_hint 为文内提及年月，不可当发布日期用",
    ]
    summary = OUT / "00_全局台账.md"
    summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n全局台账: {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
