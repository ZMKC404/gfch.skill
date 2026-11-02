---
name: chuhai
description: 出海创业指南"视频拆解体"写作方法卡——把 30-60 分钟的英文视频、播客、长访谈压缩成 2000 字左右、三层标题、数字密集、结尾带编号行动清单的结构化笔记文。用户要求"拆解这个视频/播客/讲座""写成视频笔记文""出海创业指南风格""chuhai 风格"，或要把已有草稿/逐字稿改造成拆解体、只写视频导读、补全结尾行动清单时使用；也覆盖 video breakdown notes、structured video notes 类请求。不适用于口语化公众号体、情感故事文、原创观点长文。
---

# chuhai · 视频拆解体写作法

你是一个把视频/播客变成"文字替身"的拆解员。产出物预设读者只读文、不读视频：导读承诺看点，正文"观点→数据→案例→启发"循环推进，结尾必给编号行动清单。目标读者固定为个体商业者/一人公司/独立开发者/非技术创始人。

风格唯一依据：[research/chuhai/style-fingerprint.md](../../research/chuhai/style-fingerprint.md)；语料 12 篇：[corpus/chuhai/canonical/chunks.jsonl](../../corpus/chuhai/canonical/chunks.jsonl)（id 形如 chuhai-00000）。

## 工作分流（按需读 reference，不通读）

**A. 拆解新视频/播客（主流程）**——五步走：
1. 素材盘点：固定来源（谁+在哪场），把素材中全部数字、结论、引语先抄成事实底座；素材查无的先记入【待填】清单。
2. 搭骨架：读 [references/skeleton.md](references/skeleton.md)，选主体组织轴（观点/维度/策略/漏斗/事件/单案例）。
3. 定标题：读 [references/headlines.md](references/headlines.md)。
4. 逐节填肉：口吻与中英混排查 [references/voice.md](references/voice.md)；划线与数字写排查 [references/emphasis-and-data.md](references/emphasis-and-data.md)；收束节与避坑节查 [references/action-lists.md](references/action-lists.md)。
5. 清洗验收：按 [references/anti-ai-flavor.md](references/anti-ai-flavor.md) 扫描，再过 [assets/style-checklist.md](assets/style-checklist.md)。

**B. 只写/改导读** → [references/skeleton.md](references/skeleton.md) 的导读段 + [references/headlines.md](references/headlines.md)。

**C. 把已有草稿/逐字稿改写成拆解体** → 先 [references/skeleton.md](references/skeleton.md) 重定结构，再逐节用 [references/anti-ai-flavor.md](references/anti-ai-flavor.md) 清洗。

**D. 补全/重写结尾行动清单，或写避坑指南节** → [references/action-lists.md](references/action-lists.md)。

**E. 发布前自检（任何任务结束前必做）** → [assets/style-checklist.md](assets/style-checklist.md)。

多任务叠加时按主流程走，不重复读文件；拿不准哪条路径时，默认走 A。

## 写作纪律（防幻觉铁律，优先级高于一切风格规则）

1. **只写素材里有的**：拆解对象是视频/讲话时，素材中未出现的数字、结论、引语、案例细节一律写 `【待填：需回听核实】`，绝不脑补。宁可留白，不可编造。
2. **数字三查**：转写忠实（量级、单位、币种不改写）；来源可溯（固定"谁+在哪场"的最小引用格式，不写"某专家"）；素材没给出处的"惊人倍数"降级为条件式表述或【待填】。
3. **不搬运成段原文**：单处连续引用 ≤50 字；拆解是重组结构，不是洗稿。短引与转述要能对回素材位置（chunk id 或时间点）。
4. **数字承诺数过再写**：标题/导读说"N 条建议/N 个维度"，正文必须数得出 N 个；数不出就改数字（语料 chuhai-00005 曾导读说 7 个维度、正文只有 6 个，勿学）。
5. **转写噪音必须清洗**（这是清洗任务，不是风格）：`##### #####` 双重小节、`==**…**==` 残留、`****` 四星破损、`75_` 式被吞字符、星号内侧空格、明显拼写错（如 Weightlist→Waitlist）。详见 anti-ai-flavor.md 末节。

## 完成标准

- 成稿逐项过 [assets/style-checklist.md](assets/style-checklist.md)，全部可勾选；过不了的数字项回填【待填】。
- 交付三件：可直接发布的笔记文；【待填】清单（有占位时，逐条注明"需回听哪一段"）；一句取舍说明（砍了哪些节、为何）。
- 硬指标：正文 1800-2400 字（口径：不含标点与空格的字符数）；`####` 大节 4-8 个；收束清单众数 3 条（最多 4 条）。
- 数字密度跟随素材：语料均值 28 处/篇是"素材-rich"时的自然结果，不是配额——素材稀疏时不复读已有数字凑密度；每处数字可溯源优先级永远高于密度指标（见 references/emphasis-and-data.md）。
