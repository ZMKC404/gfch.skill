#!/usr/bin/env python3
"""哥飞的朋友们群聊记录 9 包 → canonical 层（agent 原生可调用）。

用法: python3 -I tools/process_chatlog.py
输入: ~/Downloads/哥飞出海/哥飞课程/聊天记录（2024.5-2025.12）/*.zip
      每包含 1 个 <名>.html.json（WeChatMsg 导出的结构化消息列表）+ html + 图片（图片不入库）
输出: corpus/chatlog/canonical/chunks.jsonl（每条文本消息一行）+ index.md + 00_台账/
      台账含每包消息统计与源 SHA256。幂等可复跑。
消息类型（实测）: type=1 文本; 244813135921 引用/回复（xml_dict.appmsg 提 title/content）;
      3=图片 47=表情 10000=系统消息等 → 跳过，仅计数入台账。
"""
from __future__ import annotations
import hashlib, json, re, sys
from collections import Counter
from datetime import datetime
from pathlib import Path
import zipfile

REPO = Path(__file__).resolve().parent.parent
SRC = Path("/Users/venn/Downloads/哥飞出海/哥飞课程/聊天记录（2024.5-2025.12）")
OUT = REPO / "corpus/chatlog"

TYPE_MAP = {"1": "text", "244813135921": "quote", "3": "image", "47": "emoji",
            "10000": "system", "21474836529": "file?", "81604378673": "video?",
            "103079215153": "link?"}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def extract_quote(m: dict) -> tuple[str, str]:
    """引用消息: 返回 (正文, 被引用内容)。"""
    try:
        app = m["xml_dict"]["msg"]["appmsg"]
        title = (app.get("title") or "").strip()
        # 引用体在 refreopendata/refermsg content 或 title 本身
        ref = ""
        try:
            ref = (app["refreopendata"]["refermsg"]["content"] or "").strip()
        except Exception:
            pass
        body = title or (app.get("des") or "").strip()
        return body, ref
    except Exception:
        return "", ""


def clean(t: str) -> str:
    t = re.sub(r"<[^>]+>", "", t)
    return re.sub(r"\s+", " ", t).strip()


MSG_RE = re.compile(r"^\*\*(\d{2}:\d{2}:\d{2}) ([^*]+)\*\*: (.*)$")
QUOTE_RE = re.compile(r"^> ([^：:]+)[：:]\s?(.*)$")


def parse_md(z: zipfile.ZipFile) -> tuple[list[dict], int]:
    """md 版（无 json 的包）：**HH:MM:SS Speaker**: 正文 / > Speaker: 引用。"""
    mdn = [n for n in z.namelist() if n.endswith(".md")]
    if not mdn:
        return [], 0
    lines = z.read(mdn[0]).decode("utf-8", errors="replace").splitlines()
    cur_date = ""
    out = []
    for line in lines:
        d = re.match(r"^#### (\d{4}-\d{2}-\d{2})", line)
        if d:
            cur_date = d.group(1)
            continue
        m = MSG_RE.match(line)
        if m and cur_date:
            hh, speaker, body = m.group(1), m.group(2).strip(), m.group(3).strip()
            if body.startswith("!["):
                continue
            out.append({"ts": f"{cur_date} {hh}", "speaker": speaker, "text": body, "quoted": None, "type": "text"})
            continue
        q = QUOTE_RE.match(line)
        if q and out:
            out[-1]["quoted"] = clean(q.group(2))
    # 过滤空文本
    out = [r for r in out if len(r["text"]) >= 2]
    return out, len(lines)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "canonical").mkdir(exist_ok=True)
    (OUT / "00_台账").mkdir(exist_ok=True)
    records, skipped = [], Counter()
    meta_rows = ["zip,messages_total,text_msgs,quote_msgs,skipped,html_kb,json_kb"]
    for zp in sorted(SRC.glob("*.zip")):
        z = zipfile.ZipFile(zp)
        jnames = [n for n in z.namelist() if n.endswith(".html.json")]
        if not jnames:
            # 无 json 的包尝试 md 版
            md_msgs, n_lines = parse_md(z)
            for m in md_msgs:
                records.append({"id": "", "source_zip": zp.name, "ts": m["ts"],
                                "speaker": m["speaker"], "is_gefei": m["speaker"] == "哥飞",
                                "type": "text", "text": clean(m["text"]), "quoted": m["quoted"]})
            meta_rows.append(f"{zp.name},md({n_lines}lines),{len(md_msgs)},0,?,0,0")
            continue
        msgs = json.loads(z.read(jnames[0]).decode("utf-8"))
        n_text = n_quote = 0
        for m in msgs:
            t = str(m.get("type"))
            ts = datetime.fromtimestamp(m["timestamp"]).strftime("%Y-%m-%d %H:%M")
            speaker = (m.get("display_name") or "?").strip()
            body = ""
            quoted = ""
            if t == "1":
                body = clean(m.get("text") or "")
            elif t == "244813135921":
                body, quoted = extract_quote(m)
                body, quoted = clean(body), clean(quoted)
            else:
                skipped[TYPE_MAP.get(t, t)] += 1
                continue
            if len(body) < 2:
                skipped["empty"] += 1
                continue
            if t == "1":
                n_text += 1
            else:
                n_quote += 1
            records.append({
                "id": f"chat-{len(records):06d}", "source_zip": zp.name,
                "ts": ts, "speaker": speaker, "is_gefei": speaker == "哥飞",
                "type": TYPE_MAP.get(t, t), "text": body, "quoted": quoted or None,
            })
        meta_rows.append(f"{zp.name},{len(msgs)},{n_text},{n_quote},"
                         f"{len(msgs)-n_text-n_quote},0,{z.getinfo(jnames[0]).file_size//1024}")
    records.sort(key=lambda r: r["ts"])
    for i, r in enumerate(records):
        r["id"] = f"chat-{i:06d}"
    with open(OUT / "canonical/chunks.jsonl", "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    # index: 按天统计
    by_day = Counter(r["ts"][:10] for r in records)
    gefei_n = sum(1 for r in records if r["is_gefei"])
    with open(OUT / "canonical/index.md", "w", encoding="utf-8") as f:
        f.write(f"# 哥飞的朋友们群聊 · canonical 索引（{len(records)} 条文本消息，其中哥飞发言 {gefei_n} 条）\n\n")
        f.write("> 每行=一条消息（chunks.jsonl）；speaker 为群昵称，未经核实的昵称不代表真实身份；\n"
                "> 引用消息的原文在 quoted 字段；图片/表情/系统消息未入库（见台账计数）。\n\n")
        f.write("| 日期 | 消息数 |\n|---|---|\n")
        for day in sorted(by_day):
            f.write(f"| {day} | {by_day[day]} |\n")
    span = f"{records[0]['ts'][:10]} ~ {records[-1]['ts'][:10]}" if records else "无"
    top_speakers = Counter(r["speaker"] for r in records).most_common(15)
    meta = [
        "# METADATA · 哥飞的朋友们群聊（chatlog）",
        f"- 生成时间: {datetime.now().isoformat(timespec='seconds')}",
        f"- 文本消息: {len(records)} 条（时间跨度 {span}），哥飞本人 {gefei_n} 条",
        f"- 跳过: {dict(skipped)}",
        f"- 发言最多: {top_speakers}",
        "- 格式: WeChatMsg 导出 json；仅 text/quote 两类入库，图片仅存于原 zip 未提取",
        "- 注意: 群聊为口语化碎片，昵称可变，哥飞署名按导出时昵称匹配，个别重名风险已在 index 声明",
    ]
    (OUT / "00_台账/METADATA.md").write_text("\n".join(meta) + "\n", encoding="utf-8")
    (OUT / "00_台账/每包统计.csv").write_text("\n".join(meta_rows) + "\n", encoding="utf-8")
    lines = [f"{sha256(p)[:16]}…  {p.name}" for p in sorted(SRC.glob('*.zip'))]
    (OUT / "00_台账/manifest.sha256").write_text(
        "corpus/chatlog/canonical/chunks.jsonl\n".replace("^[^ ]+", "") or "", encoding="utf-8")
    with open(OUT / "00_台账/manifest.sha256", "w", encoding="utf-8") as f:
        h = hashlib.sha256((OUT / "canonical/chunks.jsonl").read_bytes()).hexdigest()
        f.write(f"{h}  canonical/chunks.jsonl\n")
        for p in sorted(SRC.glob("*.zip")):
            f.write(f"{sha256(p)}  ../../{p.name}\n")
    print(f"[ok] chatlog: {len(records)} 条文本消息 / 跨度 {span} / 哥飞 {gefei_n} 条 / 跳过 {dict(skipped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
