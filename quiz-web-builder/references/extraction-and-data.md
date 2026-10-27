# 题库数据格式与提取说明

## 1. 题库数据格式（填入 template.html 的 `const Q = [...]`）

每道题一个对象，字段：

| 字段 | 含义 |
|------|------|
| `id` | 题号（数字，用于跳题与答题卡） |
| `type` | `'choice'` 单选 / `'multi'` 多选 / `'fill'` 填空 |
| `q` | 题干文本。填空题用 `______`（≥3 个下划线）标记空位，几个空位写几个 |
| `o` | 选项文本数组（仅 choice/multi 需要，不含 `A.` 前缀） |
| `a` | 正确答案：choice 为下标数字；multi 为下标数组；fill 为可接受答案数组 |
| `ex` | 中文解析（自己撰写；原文档通常只给答案不给解析） |

示例：

```js
{id:1, type:'choice', q:'What is ...?',
 o:['A选项内容','B选项内容','C选项内容'], a:1,
 ex:'解析文字…'},

{id:2, type:'multi', q:'...?',
 o:['a','b','c'], a:[0,2], ex:'解析文字…'},

{id:3, type:'fill', q:'... ______ ...', a:['answer1','answer2'], ex:'解析…'},

{id:4, type:'fill', q:'... ______ ... ______ ...',
 a:[['空1答案A','空1答案B'], ['空2答案A']], ex:'解析…'},
```

判分规则（已内置在 template.html）：

- **choice**：所选下标 === `a`
- **multi**：所选下标集合（排序后）与 `a` 完全一致
- **fill**：每个空，输入归一化后匹配 `a[k]` 中任意一个即算该空正确；填对任一答案即可（大小写、标点、冠词忽略）。默认 `REQUIRE_ALL_BLANKS=false`：只判定已填写的空，未填的空跳过；若设为 `true` 则要求所有空都填对。
- 归一化 `norm()`：小写、去首尾空格、去常见标点、去行首冠词 the/a/an、连续空白合并为单个空格。

## 2. 文本提取（Windows 环境）

- 用 `py` 启动器而非 `python`（`python` 命令常不可用）。
- PDF 用 pdfplumber；PPTX/DOCX 用 markitdown（必要时 `py -m pip install "markitdown[docx]"`、`python-docx`）。
- 已提供 `scripts/extract.py`，一条命令导出文本：

```powershell
py scripts/extract.py "C:/path/题目.pdf" --out out.txt
```

- 常见坑：
  - 非 ASCII 路径：把路径写进 .py 脚本再运行，避免 PowerShell 传参编码问题。
  - `sys.stdout.reconfigure(encoding='utf-8')` 防止中文输出乱码。
  - PDF 是考试截图/导出页时，会混入分页数字（如右侧的 "1 2 3"、页码、`https://... 1/13`），提取后需人工剔除这些噪声，只保留题目、选项、`【答案】`。
  - PPTX 用 markitdown 会按页导出，可能混入 `<!-- Slide number -->` 注释；DOCX 的题号可能跳号（缺某题），按顺序连续编号并在页面说明即可。

## 3. 解析（ex）撰写要点

- 每题写一句中文解析：点明考点 + 判断依据。
- 选择题：说明正确项为何对，并一句带过干扰项错在哪。
- 填空题：说明句意 + 为什么填该词/短语，列出的可接受答案彼此为同义替换。
- 例：
  - 异化/归化类：指出该译名保留（异化）还是本地化（归化）了源语文化特征。
  - 直译/意译/改编类：对照"字面对应 vs 意义优先 vs 本土化改造"区分。
  - 填空类：根据空格前后语义/固定搭配（如 target audience）判断。

## 4. 生成 HTML 后的验证

1. 语法检查（Windows 无 node 也能用已装环境）：
   ```powershell
   # 提取内联 <script> 内容到 tmp.js 后：
   node --check tmp.js
   ```
2. 无头渲染验证（Edge 自带）：
   ```powershell
   & "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless --disable-gpu --virtual-time-budget=5000 --dump-dom "http://127.0.0.1:PORT/index.html"
   ```
   确认 `#stem` 有题干、`#grid` 有题目格子（说明 render() 正常执行、无 JS 报错）。
3. 判分逻辑抽测：把 `Q` 数组抽出来，用 node 模拟 `norm()` 与判分，验证填空题"填对任一答案即判对"、多空"只填部分也算对"等边界。

## 5. 本地预览

```powershell
cd 输出目录
Start-Process -WindowStyle Hidden py -ArgumentList "-m","http.server","8323"
```
然后用 `preview_url` 打开 `http://127.0.0.1:8323/index.html`。HTML 为单文件，无需后端，用户双击即可离线使用。
