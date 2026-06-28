# LLM Skill 开发仓库

一套面向大语言模型（LLM）应用的 Skill 开发框架与技能合集。

---

## 目录

```
my_skills/
├── skill_builder/           # Skill 开发助手（指导如何创建和优化 Skill）
├── tokens-auto-specialization/  # 提示词自动专业化
├── paper-read-in-depth/     # 深度阅读学术论文（7 步流程，Markdown+HTML 双输出）
├── galaxy-simulation-analyzer/  # N体盘状星系模拟快照分析工具包
├── templates/               # Skill 模板
├── skills_setup             # 批量拉取/更新外部 GitHub skills
├── tools/                   # 校验与开发工具
└── docs/                    # 开发指南
```

## 已有 Skill

| Skill | 描述 |
|-------|------|
| [skill_builder](skill_builder/SKILL.md) | Skill 开发助手——指导 Agent 设计、开发、优化和维护其他 Skill，确保产出格式规范（含 YAML frontmatter） |
| [tokens-auto-specialization](tokens-auto-specialization/SKILL.md) | 提示词自动专业化——Agent 持续激活，自动补齐角色/规则/格式/模型适配，输出精简版+顶配版 |
| [paper-read-in-depth](paper-read-in-depth/SKILL.md) | 深度阅读学术论文——自动获取内容、背景研究、提炼主线与核心证据链、技术细节分析、价值评估，输出结构化 Markdown + HTML 双格式总结 |
| [galaxy-simulation-analyzer](galaxy-simulation-analyzer/SKILL.md) | N体盘状星系模拟分析——Gadget HDF5 快照加载、坐标系变换、盘面找正与对齐、棒强度(m=2)/buckling/B&P bulge 形态学、指数标长/标高拟合、面密度剖面、Sérsic 指数拟合、3面板可视化

## 快速开始

```bash
# 1. 克隆仓库
git clone <repo-url> my_skills
cd my_skills

# 2. 部署 skills 到 ~/.agents/skills/
./skills_setup

# 3. 校验
node tools/validate.mjs
```

### 创建新 Skill

```bash
# 复制模板
cp templates/SKILL.template.md <your-skill-name>/SKILL.md

# 编辑后校验
node tools/validate.mjs
```

> **提示**：创建 Skill 时可直接问 Agent：「用 skill_builder 帮我创建一个 Skill」，Agent 会按规范自动生成。

参见 [docs/skill-development.md](docs/skill-development.md) 获取完整开发指南。

## 使用 Skill

### 一键部署全部 Skill

```bash
./skills_setup    # 拉取外部 58 个 skill + 部署本地 4 个 skill
```

### 拉取外部 Skill

```bash
./skills_setup    # 已包含在全部件中，可单独运行更新外部 skill
```

### 手动安装

```bash
cp -r <skill-id> ~/.agents/skills/<skill-id>
```

部署后在对话中通过触发词自动激活，无需手动 @。

详见 [docs/skill-development.md](docs/skill-development.md) 获取完整使用指南。

## 贡献

欢迎提交新的 Skill！请遵循以下流程：

1. 从 `templates/SKILL.template.md` 复制模板
2. 按 `docs/skill-development.md` 中的规范填写（确保 YAML frontmatter 完整）
3. 运行 `node tools/validate.mjs` 确保通过校验
4. 提交 PR

## 许可

MIT
