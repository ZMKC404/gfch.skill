# gfch.skill

出海写作风格 skill 库：语料深度处理（canonical 层，agent 原生可调用）+ 按博主分风格开发的写作 skill。一行命令安装。

## 内含 skill（不同博主不同命名）

| skill | 来源语料 | 风格定位 | 适合任务 |
|---|---|---|---|
| `gefei` | 我是哥飞公众号 552 篇（2020-2025） | 出海 SEO 实战教学体：标题先报数、教程拆到按钮级、数据到个位、夹喜报、结尾加微信 | 写建站/SEO 教程、评站报告、数据复盘、月度回顾、起标题、去 AI 腔 |
| `chuhai` | 出海创业指南 12 篇视频拆解文（未署名，拆解体） | 结构化拆解笔记体：冒号二段式标题、导读+编号小节+行动清单、划线金句、数字密度高 | 把视频/播客/长内容拆解成笔记文、写导读、改拆解体 |

## 一行安装

```bash
curl -fsSL https://raw.githubusercontent.com/ZMKC404/gfch.skill/main/install.sh | bash
```

raw.githubusercontent 直连不通时（网络环境原因），任选一个镜像入口，install.sh 内部也会自动回退下载源：

```bash
curl -fsSL https://fastly.jsdelivr.net/gh/ZMKC404/gfch.skill@main/install.sh | bash
curl -fsSL https://ghproxy.net/https://raw.githubusercontent.com/ZMKC404/gfch.skill/main/install.sh | bash
```

要锁定版本（镜像对 @main 有分钟级缓存，刚发新版时可改用 tag 入口，永不缓存过期）：

```bash
curl -fsSL https://fastly.jsdelivr.net/gh/ZMKC404/gfch.skill@v1.0/install.sh | bash
```

只装其中一个：

```bash
curl -fsSL https://raw.githubusercontent.com/ZMKC404/gfch.skill/main/install.sh | bash -s -- gefei
curl -fsSL https://raw.githubusercontent.com/ZMKC404/gfch.skill/main/install.sh | bash -s -- chuhai
```

安装到已存在的 `~/.zcode/skills/`、`~/.claude/skills/`、`~/.codex/skills/`（都没有则装到 `~/.claude/skills/`）。新开会话后直接说人话触发。

## 用法示例

- gefei：「按哥飞的口吻写一篇我的新站上线 30 天复盘」「帮我评一下这个工具站的 SEO，按哥飞评站报告的格式」
- chuhai：「把这份访谈笔记拆解成一篇出海创业指南体的文章」「给这篇拆解文写导读和行动清单」

## 仓库结构

```
skills/gefei/        SKILL.md（最小路由器）+ references/6 + assets/自检表
skills/chuhai/       SKILL.md（最小路由器）+ references/6 + assets/自检表
corpus/gefei/        canonical/chunks.jsonl（552 篇全文）+ index.md + 图片索引与实读转写 + 台账
corpus/chuhai/       canonical/chunks.jsonl（12 篇全文）+ index.md + 台账
corpus/chatlog/      群聊 25,323 条消息（哥飞 3,854 条，2025-08~12 实战口径层）
corpus/robin/        罗宾出海 SOP 4 件（话术/邮件/合同/SOP 总纲）
corpus/00_视频台账.md 视频 73+ 个 / 25.4GB 全量登记（未转写）
research/            风格指纹 + 代表性原文样例（skill 的唯一风格依据）
tools/               语料处理脚本（幂等可复跑）
_work/盲测/          盲测写样与自评（验收证据）
docs/                验收报告
```

## 质量纪律

- 语料：原始 zip 零改动（SHA256 入台账），canonical 层清洗规则见 `tools/process_corpus.py` 头注释；剔除 63 篇"阅读全文"占位文。
- 防幻觉：skill 强制【待填】占位制——任何数字/事实必须可溯源（素材给定 / 语料原文 / 【待填】占位），盲测验证 0 编造数据点。
- 引文核验：skill 内全部正例短引逐字回源核验（对抗审查 148 条 + 开发期 227 条），chunk id 全部实存。
- 归因分层：通用 SEO 知识（sitemap/外链等）不署哥飞名；"养网站防老""新词新站""饱和式建站"等哥飞自创概念才署名。

## 已知边界（如实登记）

- 哥飞课程视频（上海分享 8 个 Web.Cafe.ts、年中分享会 mp4 等）未转写：成本高且与公众号语料重叠，台账登记后续可补。
- 公众号导出只保留了每篇封面图，正文中 SEO 截图未随导出保留（图片层 47 张实读结论），已记台账缺口。
- chuhai 语料作者未署名，如实标注不猜测。

## 许可

skill 方法卡部分 MIT；语料文本版权归原作者所有，仅供学习研究，不得商用或冒名发布。
