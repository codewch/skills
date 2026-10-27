# 中英对照 HTML 格式规范（英→中）

本文件是产出 HTML 的详细规范。正文翻译以 `assets/template.html` 为骨架，本文件补充每种元素的写法、翻译准则与已知坑位。

## 1. 页面结构顺序（从上到下）

1. `<head>`：标题 + 完整 `<style>`（复用模板，勿改）
2. `<div class="progress">` + `<header class="toolbar">`（复用模板，勿改）
3. `.shell` 内：
   - `<nav class="sidebar">`：目录（`摘要` + 各节 + `参考文献` + `术语对照`）
   - `<main class="paper">`：
     - `.kicker`（期刊/卷期/页码/DOI）
     - `h1.zh`（中文标题）+ `.title-en.en`（英文标题）
     - `.byline`（作者）
     - `.metadata`（单位逐条 `.pair`；收稿/接收日期与原文链接）
     - `.reader-note`（译稿说明）
     - `#abstract`（摘要 `.pair`）
     - 关键词 `.pair`
     - 正文：`h2`/`h3`/`h4` 标题 + `article.block.pair` 段落 + `section.visual` 图/表
     - `#refs` 参考文献 + `#glossary` 术语表 + `.footer`
4. 末尾 `<script>`（复用模板，勿改）

## 2. 各元素写法

### 段落（逐段对照，核心）
每个原文段落独立成一个 `.block.pair`，左 `.en`（英文原文）、右 `.zh`（中文译文）。**不要**把多个段落合并到一个 pair，也不要整节打包翻译。

```html
<article class="block p" id="bN"><a class="page-link" href="{pdf文件名}#page=N">原文第 N 页 ↗</a><div class="pair "><div class="en" lang="en"><p>ENGLISH</p></div><div class="zh" lang="zh-CN"><p>中文译文</p></div></div></article>
```

### 标题
`h2`/`h3`/`h4` 内放两个 span：`<span class="zh">中文</span><span class="en heading-en">English</span>`。语言切换按钮依赖 `.en`/`.zh` 类，不要省略。

```html
<h2 id="s1"><span class="zh">1 引言</span><span class="en heading-en">Introduction</span></h2>
```

### 图
从 PDF 提取**原图**内嵌（占位符 `{{FIGn}}`），不要外链、不要占位图、不要用文字描述替代。

```html
<section class="visual" id="fig1" aria-label="图 1：中文图题"><div class="pair caption"><div class="en" lang="en"><p>Fig.1 English caption</p></div><div class="zh" lang="zh-CN"><p>图 1：中文图题</p></div></div><img class="chart" src="data:image/jpeg;base64,{{FIG1}}" alt="图 1：中文图题"></section>
```

### 表
保留原数值；表头单元格用 `"English / 中文"` 双语格式；`.table-scroll` 包 `<table>`。

### 参考文献
每条一个 `.block.ref`：左英文完整原文，右 `[n] 题名译文：...`。作者、期刊名、卷期页码保留原文。

```html
<article class="block ref" id="rN"><a class="page-link" href="{pdf文件名}#page=N">原文第 N 页起 ↗</a><div class="pair "><div class="en" lang="en"><p>Author, A., 2020. Title. Journal, 1(2): 3-4.</p></div><div class="zh" lang="zh-CN"><p>[N] 题名译文：《标题译文》</p></div></div></article>
```

### 术语表
`details.glossary` + `summary` + `dl`，每项 `dt`（术语/英文）配 `dd`（解释）。抽取本文 15~25 个专业术语。

## 3. 翻译准则

- 方向固定 **英→中**；英文段落逐字保留原文（不要改写英文）。
- **数值、单位、公式、指标一律保留**：如 `R² = 0.86`、`Kappa 0.84`、`Δθ`、`SSC = -294.84 × A21 + 79.401`、`10 m × 10 m`、`1∶50,000`。
- **引文 `(作者, 年份)` 保留原文**：如 `(Cheng, 2018, 2021)`，不翻译。
- **专有名词/术语**：首次出现可附英文，如「主成分分析（PCA）」。
- **作者中文名**：只音译 100% 确定的名字（如 CHENG Qiuming → 成秋明）；不确定的保留拼音。
- 译文用自然、专业的中文，避免生硬直译。

## 4. 常见坑位

1. **两栏排版串行**：期刊 PDF 多为双栏，提取文字时先读左栏、再读右栏。`scripts/extract_pdf.py` 已按左/右/全宽分区输出，照着 `TOP/FULL-WIDTH`、`LEFT COLUMN`、`RIGHT COLUMN` 顺序阅读即可。
2. **插图格式**：部分 PDF 内嵌图为 jpx/JPEG2000，浏览器不支持；`extract_pdf.py` 已统一转 JPEG。
3. **图片体积**：控制单图宽 ≤1400px、JPEG quality ≈85，总 HTML 控制在几 MB。不要内嵌未压缩的 PNG 大图。
4. **参考文献提取不全**：双栏参考文献页可能截断。若某条正文引用（如 `(Gong et al., 2004)`）在参考文献列表找不到完整书目，**不要杜撰卷期页码**，用 `.editor-note` 标注「以原刊为准」。
5. **占位符**：图用 `{{FIGn}}`（n 从 1 起），与 `images/FigN.jpg` 文件名对应；注入后确保无残留占位符。
6. **中文文件名**：预览时 URL 中的中文/空格需百分号编码。
7. **校验**：生成后启动本地 HTTP 服务预览，检查图片显示、目录跳转、三种语言模式（中英对照/仅中文/仅英文）切换、打印样式。
