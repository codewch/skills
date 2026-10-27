---
name: quiz-web-builder
description: 将包含题目与答案的学习/测试材料（PDF、PPTX、DOCX 等）转换成可交互的单文件 HTML 答题网页。当用户提供试卷、复习题、自测题、讲义习题等文档，并要求「做成答题网页 / 生成答题网页 / 把题目做成 HTML / 错题解析 / 收藏 / 笔记」等时，应使用本 skill。它负责提取题目、为每道题补写解析，并套用内置模板生成支持逐题提交查看答案解析、错题筛选、收藏筛选、逐题笔记的网页。
---

# Quiz Web Builder

## 用途

把「题目 + 参考答案」类文档转成单文件、离线可用的 HTML 答题网页。网页自带：逐题提交后显示答案与解析、填空题任一可接受答案即判对、错题筛选、收藏筛选、逐题笔记、答题进度统计。

## 使用时机

- 用户 @ 引用一个 PDF / PPTX / DOCX，要求做成答题网页、在线做题、错题本、含收藏/笔记的复习工具。
- 用户给出题目文本或截图，要求生成可交互答题页面。

## 工作流程

按顺序执行以下步骤。

### 1. 提取题目文本

用 `scripts/extract.py` 提取文本（见 `references/extraction-and-data.md` 第 2 节）：

```powershell
py scripts/extract.py "C:/path/材料.pdf" --out out.txt
```

PDF 用 pdfplumber，PPTX/DOCX 用 markitdown（缺依赖先 `py -m pip install "markitdown[docx]" python-docx pdfplumber`）。

阅读提取结果，逐题还原：题号、题干、选项（如有）、正确答案。剔除分页数字、页码、URL 等噪声。若原文档题号跳号，按顺序连续编号即可，并在页面副标题说明。

### 2. 整理题库数据 + 撰写解析

按 `references/extraction-and-data.md` 第 1 节的格式，整理出 `Q` 数组：

- 判断题目的题型：单选 `choice`、多选 `multi`、填空 `fill`（空位用 `______` 标记）。
- 填空题：把参考答案按 `;` 拆成可接受答案数组；多空题用「数组的数组」对应每个空。
- **为每题撰写中文解析 `ex`**：原文档通常只有答案，解析需自己补写（要点见 reference 第 3 节）。

### 3. 套用模板生成网页

1. 复制 `assets/template.html` 到输出目录（如 `c:/Users/.../quiz/index.html`）。
2. 填入 `Q` 数组；设置顶部 `TITLE` / `SUBTITLE` / `STORE_KEY`（不同试卷用不同值，避免本地记录串扰）。
3. 按需调整 `REQUIRE_ALL_BLANKS`（默认 false = 已填的空正确即算对，未填跳过）。

### 4. 验证

按 `references/extraction-and-data.md` 第 4 节验证：

- `node --check` 检查内联脚本语法。
- 用无头 Edge `--dump-dom` 确认页面正常渲染（`#stem`、`#grid` 有内容）。
- 用 node 抽测判分边界（填空填任一答案判对、多空只填部分也算对）。

### 5. 预览与交付

按 reference 第 5 节启动 `python -m http.server` 并用 `preview_url` 预览。向用户说明文件路径与已实现功能。

## 关键约定

- **填空题判分**：任一可接受答案即判对；归一化忽略大小写、标点、行首冠词。
- **单文件交付**：HTML 内联全部 CSS/JS 与题库，双击即可离线打开，无需后端。
- **数据持久化**：答题记录、收藏、笔记存 localStorage（`STORE_KEY` 区分不同试卷）。
- **解析必须补写**：题目来源文档往往只有「答案」没有「解析」，不要留空。

## 资源

- `scripts/extract.py` — 一条命令从 PDF/PPTX/DOCX 提取文本。
- `assets/template.html` — 完整答题网页模板（含三种题型 + 全部功能），替换 `Q` 数组即可用。
- `references/extraction-and-data.md` — 数据格式、判分规则、提取坑点、验证方法、解析撰写要点。
