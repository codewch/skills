# skills

CodeBuddy 技能（Skill）集合。每个子目录是一个独立技能，克隆后放入 `~/.codebuddy/skills/` 即可被 CodeBuddy 自动加载。

## 技能索引

| 技能 | 说明 | 主要输入 |
|------|------|----------|
| [paper-bilingual-html](./paper-bilingual-html/) | 英文论文 PDF 翻译为「中英对照 HTML」阅读译稿，逐段对照、保留原图、附术语表 | 英文论文 PDF |
| [quiz-web-builder](./quiz-web-builder/) | 试题材料做成可交互答题网页，逐题提交查答案解析，支持错题筛选、收藏、笔记 | PDF / PPTX / DOCX |

---

## 一、技能目录规范

每个技能是仓库根目录下的一个文件夹，**文件夹名即技能名**，必须与 `SKILL.md` 中 `name` 字段完全一致。

```
<skill-name>/
├── SKILL.md              # 必需，技能的唯一入口
├── assets/               # 可选，模板、样式、示例等静态资源
├── scripts/              # 可选，可执行脚本（Python / Shell / Node）
└── references/           # 可选，详细文档，供 SKILL.md 按需引用
```

### 命名规范

- 全小写，单词间用连字符 `-`，例如 `quiz-web-builder`
- 只用字母、数字、连字符，长度 ≤ 64 字符
- **使用动名词或名词性短语**，能直接看出能力，避免 `tool1`、`test`、`my-skill` 这类无意义名字
- 一个技能只解决一类任务，不要做成「万能助手」

### SKILL.md 规范

文件必须以 YAML frontmatter 开头，仅两个字段：

```markdown
---
name: quiz-web-builder
description: 将包含题目与答案的学习/测试材料（PDF、PPTX、DOCX 等）转换成可交互的单文件 HTML 答题网页。当用户提供试卷、复习题、自测题、讲义习题等文档，并要求「做成答题网页 / 生成答题网页 / 把题目做成 HTML / 错题解析 / 收藏 / 笔记」等时，应使用本 skill。它负责提取题目、为每道题补写解析，并套用内置模板生成支持逐题提交查看答案解析、错题筛选、收藏筛选、逐题笔记的网页。
---
```

| 字段 | 要求 |
|------|------|
| `name` | 与文件夹名一致；小写连字符（见上） |
| `description` | **最关键**。第三人称书写，回答三件事：**做什么 + 什么时候用 + 能产出什么**。要把用户可能说的原话（触发词）写进去，这是技能被自动调用的唯一依据；长度 ≤ 1024 字符 |

正文用 Markdown，建议结构：

```markdown
# 技能名

## 用途              —— 一句话说清能力边界
## 使用时机          —— 什么情况下该用它
## 工作流程          —— 分步骤、可执行，命令写全（用 py 而非 python 等）
## 关键约定          —— 易踩坑的硬性规则
## 资源              —— assets / scripts / references 各是什么、怎么用
```

### 内容编写原则

- **SKILL.md 保持精简**，只放「路由 + 流程骨架」；长篇细节、格式规范、字段表放进 `references/`，在 SKILL.md 里指路即可
- **把踩过的坑写进技能**：依赖缺失、编码问题、非 ASCII 路径、判分边界等，写清「现象 → 正确做法」
- **命令必须可直接运行**：写清工作目录、参数、依赖安装方式，不要留 `<占位>` 之外的空洞
- 不要把某一次任务的**具体数据**写进技能（如某份试卷的 50 道题），只写**可复用的方法与模板**

### 体积与文件限制

- 单个技能建议 < 5 MB；模板类大文件（HTML/CSS/图片）控制在几百 KB 内
- 二进制资源（图片、字体、样例 PDF）尽量少，能用脚本生成的不要提交
- 不提交：`.DS_Store`、`__pycache__/`、`*.pyc`、`.venv/`、`node_modules/`、临时日志

---

## 二、上传（发布）规范

### 提交前自检清单

- [ ] 文件夹名 = `SKILL.md` 的 `name` 字段
- [ ] frontmatter 只有 `name`、`description` 两个字段，且 description 含明确的触发场景
- [ ] `SKILL.md` 里引用的每个 `assets/` / `scripts/` / `references/` 路径都真实存在
- [ ] 脚本无语法错误（`py -m py_compile scripts/xxx.py`、`node --check xxx.js`）
- [ ] 至少跑通一次真实任务，确认产出可用
- [ ] 本 README 的「技能索引」表已加入新技能
- [ ] 没有夹带密钥、token、个人隐私数据

### 提交流程

```bash
git clone https://github.com/codewch/skills.git
cd skills

# 1. 新建技能目录，按上面的结构放入文件
# 2. 更新 README 技能索引表
# 3. 校验 + 提交 + 推送
git add -A
git status --short          # 确认只包含本次技能相关文件
git commit -m "feat(<skill-name>): add <一句话说明>"
git push origin main
```

### 提交信息规范

采用 `类型(技能名): 说明` 格式：

| 类型 | 用途 | 示例 |
|------|------|------|
| `feat` | 新增技能 | `feat(quiz-web-builder): add quiz web builder skill` |
| `fix` | 修复技能缺陷 | `fix(quiz-web-builder): 填空题任一答案即判对` |
| `docs` | 只改文档 | `docs: 补充技能上传与安装规范` |
| `refactor` | 调整结构不改行为 | `refactor(paper-bilingual-html): 拆分 references` |
| `chore` | 仓库维护 | `chore: 添加 .gitignore` |

一次提交只做一件事；新增技能时，技能目录与 README 索引表放在同一个提交里。

---

## 三、安装（使用）规范

技能目录位置：

| 系统 | 路径 |
|------|------|
| Windows | `C:\Users\<用户名>\.codebuddy\skills\` |
| macOS / Linux | `~/.codebuddy/skills/` |

安装后目录形如 `.codebuddy/skills/quiz-web-builder/SKILL.md`，**多套一层或少了 SKILL.md 都不会被识别**。

### 方式一：git clone（推荐，便于更新）

```bash
git clone https://github.com/codewch/skills.git ~/skills-repo

# 复制需要的技能（Windows PowerShell）
Copy-Item -Recurse -Force "$HOME\skills-repo\quiz-web-builder" "$HOME\.codebuddy\skills\"

# macOS / Linux
cp -r ~/skills-repo/quiz-web-builder ~/.codebuddy/skills/
```

更新：

```bash
cd ~/skills-repo && git pull
# 再执行一次上面的复制命令覆盖安装
```

### 方式二：整仓拷贝（一次装全部）

```powershell
git clone https://github.com/codewch/skills.git "$HOME\.codebuddy\skills-tmp"
Copy-Item -Recurse -Force "$HOME\.codebuddy\skills-tmp\*" "$HOME\.codebuddy\skills\"
Remove-Item -Recurse -Force "$HOME\.codebuddy\skills-tmp"
```

注意：整仓拷贝会把 README.md 也带进去，无害但不必要，克隆后只复制技能子目录即可。

### 方式三：手动下载

打开仓库页面 → 进入技能目录 → `Download ZIP`，解压后把**技能文件夹本身**放到 `~/.codebuddy/skills/` 下（不要保留 `skills-main/` 这类外层目录）。

### 安装后验证

1. 确认路径正确：`~/.codebuddy/skills/<skill-name>/SKILL.md` 存在
2. 新开一个 CodeBuddy 会话，问「你现在有哪些 skills」或直接描述任务触发它
3. 若未加载：检查文件夹名与 `name` 是否一致、frontmatter 是否有 `---` 包裹、是否多套了一层目录

### 卸载与更新

- **卸载**：删除 `~/.codebuddy/skills/<skill-name>/` 整个目录即可，无残留、无注册表项
- **更新**：用新版本覆盖同名目录；若技能数据结构变更，注意提醒用户清理本地 `localStorage` 之类由技能产出的缓存数据

---

## 四、版本与兼容

- 技能无独立版本号，以仓库提交历史为准
- 破坏性变更（如输出数据结构调整）需在 `commit` 说明中显式标注 `BREAKING CHANGE`
- 技能依赖的外部库（如 `pdfplumber`、`pymupdf`）应在 `SKILL.md` 中写明安装命令，不要假设已预装

## 五、许可

仓库内技能仅用于个人学习与教学场景，按需自取。引用他人代码或模板时请注明来源。
