> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`.claude/skills/contribute/SKILL.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

---
name: contribute
description: "贡献 Trellis 文档与 marketplace 的指南。覆盖添加 spec 模板、marketplace skills、文档页面，以及向 Trellis 主仓与 docs 仓提交 PR。在有人想新增 spec 模板、向 marketplace 加 skill、增改文档页，或向本项目提 PR 时使用。"
---

# 为 Trellis 做贡献（Contributing to Trellis）

贡献拆在两个仓库：

| 内容 | 仓库 | 用途 |
|------|------|---------|
| 文档页面 | [mindfold-ai/docs](https://github.com/mindfold-ai/docs) | Mintlify 文档站 |
| Skills + Spec 模板 | [mindfold-ai/Trellis](https://github.com/mindfold-ai/Trellis) | `marketplace/` 目录 |

## Docs 仓结构

```
docs/
├── docs.json              # Navigation config (MUST update for new pages)
│
├── index.mdx              # English homepage
├── quickstart.mdx         # English quickstart
├── zh/index.mdx           # Chinese homepage
├── zh/quickstart.mdx      # Chinese quickstart
│
├── guides/                # English guide pages
├── zh/guides/             # Chinese guide pages
│
├── templates/             # English template pages
├── zh/templates/          # Chinese template pages
│
├── skills-market/         # English skill marketplace pages
├── zh/skills-market/      # Chinese skill marketplace pages
│
├── blog/                  # English tech blog
├── zh/blog/               # Chinese tech blog
│
├── changelog/             # English changelog
├── zh/changelog/          # Chinese changelog
│
├── contribute/            # English contribution guide
├── zh/contribute/         # Chinese contribution guide
│
├── showcase/              # English showcase
└── zh/showcase/           # Chinese showcase
```

## Trellis 主仓 Marketplace 结构

```
marketplace/
├── index.json             # Template registry (lists all available templates)
├── README.md              # Marketplace overview
├── specs/                 # Spec templates
│   └── electron-fullstack/
│       ├── README.md
│       ├── frontend/
│       ├── backend/
│       ├── guides/
│       └── shared/
└── skills/                # Skills
    └── trellis-meta/
        ├── SKILL.md
        └── references/
```

## 理解 docs.json

导航采用 **按语言划分** 的结构：

```json
{
  "navigation": {
    "languages": [
      {
        "language": "en",
        "groups": [
          {
            "group": "Getting started",
            "pages": ["index", "quickstart"]
          },
          {
            "group": "Guides",
            "pages": ["guides/specs", "guides/tasks", ...]
          },
          {
            "group": "Resource Marketplace",
            "pages": [
              {
                "group": "Skills",
                "expanded": false,
                "pages": ["skills-market/index", "skills-market/trellis-meta"]
              },
              {
                "group": "Spec Templates",
                "expanded": false,
                "pages": ["templates/specs-index", "templates/specs-electron"]
              }
            ]
          }
        ]
      },
      {
        "language": "zh",
        "groups": [
          // Same structure with zh/ prefix
        ]
      }
    ]
  }
}
```

**要点**：

- 英文页面：无前缀（例如 `guides/specs`）
- 中文页面：`zh/` 前缀（例如 `zh/guides/specs`）
- 支持嵌套 group（例如 Resource Marketplace 下的 Skills）
- `expanded: false` 默认折叠分组

## 贡献 Spec 模板

Spec 模板在 **Trellis 主仓** 的 `marketplace/specs/`。

### 1. 创建模板目录

```
marketplace/specs/your-template-name/
├── README.md              # Template overview (required)
├── frontend/              # Frontend guidelines
│   ├── index.md
│   └── ...
├── backend/               # Backend guidelines
│   ├── index.md
│   └── ...
├── guides/                # Thinking guides
│   └── ...
└── shared/                # Cross-cutting concerns (optional)
    └── ...
```

结构随技术栈变化。按模板相关性包含目录即可。

### 2. 在 index.json 注册

把模板加入 Trellis 仓的 `marketplace/index.json`：

```json
{
  "id": "your-template-id",
  "type": "spec",
  "name": "Your Template Name",
  "description": "Brief description of the template",
  "path": "marketplace/specs/your-template-name",
  "tags": ["relevant", "tags"]
}
```

### 3. 创建文档页（两种语言，在 docs 仓）

**English**: `templates/specs-your-template.mdx`  
**Chinese**: `zh/templates/specs-your-template.mdx`

使用此 frontmatter：

```yaml
---
title: 'Your Template Name'
description: 'Brief description'
---
```

### 4. 更新 docs.json 导航

找到 `Spec Templates` 嵌套 group，加入你的页面：

```json
{
  "group": "Spec Templates",
  "expanded": false,
  "pages": ["templates/specs-index", "templates/specs-electron", "templates/specs-your-template"]
}
```

中文在 `"language": "zh"` 下同样处理：

```json
{
  "group": "Spec Templates",
  "expanded": false,
  "pages": [
    "zh/templates/specs-index",
    "zh/templates/specs-electron",
    "zh/templates/specs-your-template"
  ]
}
```

### 5. 更新总览页

把模板加入下列表格：

- `templates/specs-index.mdx`
- `zh/templates/specs-index.mdx`

## 贡献 Skill

Skills 在 **Trellis 主仓** 的 `marketplace/skills/`。

### 1. 创建 skill 目录

```
marketplace/skills/your-skill/
├── SKILL.md               # Skill definition (required)
└── references/            # Reference docs (optional)
```

`SKILL.md` 格式见 [Claude Code Skills documentation](https://code.claude.com/docs/en/skills)。

### 2. 在 index.json 注册

把 skill 加入 Trellis 仓的 `marketplace/index.json`：

```json
{
  "id": "your-skill-id",
  "type": "skill",
  "name": "Your Skill Name",
  "description": "Brief description",
  "path": "marketplace/skills/your-skill",
  "tags": ["relevant", "tags"]
}
```

### 3. 创建文档页（docs 仓）

**English**: `skills-market/your-skill.mdx`  
**Chinese**: `zh/skills-market/your-skill.mdx`

### 4. 更新 docs.json 导航

找到 `Skills` 嵌套 group，两种语言都加入你的页面。

### 5. 更新总览页

把 skill 加入表格：

- `skills-market/index.mdx`
- `zh/skills-market/index.mdx`

### 安装

用户通过以下方式安装 skills：

```bash
npx skills add mindfold-ai/Trellis/marketplace -s your-skill
```

## 贡献 Showcase 项目

### 1. 复制模板

```bash
cp showcase/template.mdx showcase/your-project.mdx
cp zh/showcase/template.mdx zh/showcase/your-project.mdx
```

### 2. 填写项目详情

- 用项目名更新 `sidebarTitle`
- 添加项目描述
- 把 GitHub OG 图 URL 换成你的仓库
- 描述你如何使用 Trellis

### 3. 更新 docs.json 导航

找到 `Showcase` / `项目展示` group，加入你的页面：

```json
{
  "group": "Showcase",
  "expanded": false,
  "pages": ["showcase/index", "showcase/open-typeless", "showcase/your-project"]
}
```

中文同样操作。

### 4. 在总览页加 Card

用 Card 组件展示你的项目：

**English** (`showcase/index.mdx`):

```mdx
<Card title="Project Name" icon="icon-name" href="/showcase/your-project">
  One-line description
</Card>
```

**Chinese** (`zh/showcase/index.mdx`):

```mdx
<Card title="项目名" icon="icon-name" href="/zh/showcase/your-project">
  一句话描述
</Card>
```

## 贡献文档

### 新增 guide

1. 在 `guides/your-guide.mdx` 创建页面
2. 在 `zh/guides/your-guide.mdx` 创建中文版
3. 更新 `docs.json` —— 两种语言都加入 `Guides` group

### 新增 blog post

1. 在 `blog/your-post.mdx` 创建页面
2. 在 `zh/blog/your-post.mdx` 创建中文版
3. 更新 `docs.json` —— 两种语言都加入 `Tech Blog` group

### 更新既有页面

1. 在对应目录找到文件
2. 做修改
3. 确保两种语言版本保持同步

## 双语要求（Bilingual Requirements）

**所有面向用户的内容必须同时有英文与中文版本。**

| 内容类型 | 英文路径 | 中文路径 |
| ------------ | --------------------- | ------------------------ |
| Homepage     | `index.mdx`           | `zh/index.mdx`           |
| Guides       | `guides/*.mdx`        | `zh/guides/*.mdx`        |
| Templates    | `templates/*.mdx`     | `zh/templates/*.mdx`     |
| Skills       | `skills-market/*.mdx` | `zh/skills-market/*.mdx` |
| Showcase     | `showcase/*.mdx`      | `zh/showcase/*.mdx`      |
| Blog         | `blog/*.mdx`          | `zh/blog/*.mdx`          |
| Changelog    | `changelog/*.mdx`     | `zh/changelog/*.mdx`     |

## 开发环境搭建

```bash
# Install dependencies
pnpm install

# Start local dev server
pnpm dev

# Check markdown lint
pnpm lint:md

# Verify docs structure
pnpm verify

# Format files
pnpm format
```

**Pre-commit hooks**：项目使用 husky + lint-staged。提交时：

- Markdown 自动 lint 与格式化
- `verify-docs.py` 检查 docs.json 与 frontmatter

## MDX 组件

Mintlify 支持 MDX 组件。常用：

```mdx
<Card title="Title" icon="download" href="/path">
  Card content here
</Card>

<CardGroup cols={2}>
  <Card>...</Card>
  <Card>...</Card>
</CardGroup>

<Accordion title="Click to expand">Hidden content</Accordion>

<AccordionGroup>
  <Accordion>...</Accordion>
</AccordionGroup>
```

允许内联 HTML（MDX）。全部组件见 [Mintlify docs](https://mintlify.com/docs/components)。

## 提交 PR

**文档改动**（docs 仓）：

1. Fork: `https://github.com/mindfold-ai/docs`
2. Clone: `git clone https://github.com/YOUR_USERNAME/docs.git`
3. Install: `pnpm install`
4. Branch: `git checkout -b feat/your-contribution`
5. 按本指南修改
6. Test: `pnpm dev`
7. 用 conventional message 提交（例如 `docs: add xxx template`）
8. Push 并创建 PR

**skills/spec 模板**（Trellis 仓）：

1. Fork: `https://github.com/mindfold-ai/Trellis`
2. Clone: `git clone https://github.com/YOUR_USERNAME/Trellis.git`
3. 在 `marketplace/` 下添加 skill/template
4. 更新 `marketplace/index.json`
5. Push 并创建 PR

## PR 前检查清单

- [ ] 已创建 EN 与 ZH 两个版本（文档页）
- [ ] 两种语言的 `docs.json` 已更新（文档页）
- [ ] `marketplace/index.json` 已更新（skills/templates）
- [ ] 总览/index 页已加入新条目
- [ ] 本地预览已测（`pnpm dev`）
- [ ] 无坏链
- [ ] 代码块语言标签正确
- [ ] frontmatter 含 title 与 description
- [ ] 图片放在 `images/` 目录（若有）
