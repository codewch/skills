---
name: paper-bilingual-html
description: 将英文论文 PDF 翻译为「中英对照 HTML」阅读译稿（固定方向英→中）。当用户提供英文论文 PDF，并要求「翻译论文 / 做成中英对照 HTML / 双语对照阅读版 / 翻译成中文网页」等，或希望产出逐段英中对照、保留原图、含术语表与参考文献译文的网页时，应使用此技能。它处理 PDF 两栏文字提取、插图转 base64 内嵌，并复用一套固定的工具栏/双栏对照样式。
---

# Paper Bilingual HTML

## Overview

把一篇英文论文 PDF 产出为自包含的中英对照 HTML：正文逐段英中对照、图表保留原图内嵌、参考文献逐条配题名译文、附术语表，并带「中英对照 / 仅中文 / 仅英文」切换与打印导出等工具栏。

## Workflow

按顺序执行以下步骤。

### Step 1: 确认输入

- 定位待翻译的英文 PDF（唯一必需输入）。
- 若用户另给了「格式示例 HTML」，以其为模板；否则使用本技能内置的 `assets/template.html`。

### Step 2: 提取文本与插图

运行 `scripts/extract_pdf.py` 完成两栏文字重建与插图转 JPEG：

```bash
py scripts/extract_pdf.py "<论文.pdf>" --out "<工作目录>"
```

产物：
- `<工作目录>/extracted_text.txt` — 按「全宽/左栏/右栏」分区重建的正文
- `<工作目录>/images/FigN.jpg` — 转码后的插图
- `<工作目录>/images_manifest.txt` — 图与页码/尺寸对照（用于把图对应到图题）

脚本依赖 `pymupdf` 与 `Pillow`，缺失时先 `pip install pymupdf Pillow`。若 PDF 为单栏或非 A4 版式，按脚本顶部注释调整分栏阈值。

### Step 3: 阅读并逐段翻译

- 通读 `extracted_text.txt`，按 `TOP/FULL-WIDTH` → `LEFT COLUMN` → `RIGHT COLUMN` 顺序理解每页内容。
- 固定英→中逐段翻译。详细格式、元素写法与翻译准则见 `references/format-spec.md`。

### Step 4: 组装 HTML

以 `assets/template.html` 为骨架，逐段填入 `.pair`（左 `.en` 英文原文 / 右 `.zh` 中文译文）。插入图时用占位符 `{{FIG1}}`…`{{FIGn}}` 对应 `images/FigN.jpg`。完整结构顺序与每种元素的写法见 `references/format-spec.md`。

### Step 5: 注入图片

运行 `scripts/build_html.py` 将 base64 图片写入最终 HTML：

```bash
py scripts/build_html.py "<模板或半成品.html>" "<工作目录>/images" "<输出.html>"
```

确认无残留 `{{FIGn}}` 占位符。

### Step 6: 预览校验

- 启动本地 HTTP 服务（如 `py -m http.server 8765 --directory <输出目录>`），用浏览器打开最终 HTML。
- 校验：图片正常显示、目录锚点跳转、三种语言模式切换、「上下对照」布局、打印样式。

## Resources

- `scripts/extract_pdf.py` — 两栏文本重建 + 插图转 JPEG
- `scripts/build_html.py` — base64 图片注入
- `assets/template.html` — 含固定 CSS/JS 的 HTML 骨架
- `references/format-spec.md` — 结构顺序、元素写法、翻译准则与常见坑位
