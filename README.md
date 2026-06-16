# LLM Skill 开发仓库

一套面向大语言模型（LLM）应用的 Skill 开发框架与技能合集。

---

## 目录

```
my_skills/
├── skill_builder/           # Skill 开发助手（指导如何创建和优化 Skill）
├── tokens-auto-specialization/  # 提示词自动专业化
├── templates/               # Skill 模板
├── tools/                   # 校验与开发工具
└── docs/                    # 开发指南
```

## 已有 Skill

| Skill | 描述 |
|-------|------|
| [skill_builder](skill_builder/SKILL.md) | Skill 开发助手——指导 Agent 设计、开发、优化和维护其他 Skill，确保产出格式规范（含 YAML frontmatter） |
| [tokens-auto-specialization](tokens-auto-specialization/SKILL.md) | 提示词自动专业化——Agent 持续激活，自动补齐角色/规则/格式/模型适配，输出精简版+顶配版 |

## 快速开始

```bash
# 1. 克隆仓库
git clone <repo-url> my_skills
cd my_skills

# 2. 部署 skills 到 ~/.agents/skills/
./setup

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

每个 Skill 可通过以下方式使用：

```bash
# 1. 将 skill 目录复制/链接到 ~/.agents/skills/ 目录下
cp -r <skill-id> ~/.agents/skills/<skill-id>

# 2. 在对话中通过触发词自动激活 Skill（无需手动 @）
```

详见 [docs/skill-development.md](docs/skill-development.md) 获取完整使用指南。

## 贡献

欢迎提交新的 Skill！请遵循以下流程：

1. 从 `templates/SKILL.template.md` 复制模板
2. 按 `docs/skill-development.md` 中的规范填写（确保 YAML frontmatter 完整）
3. 运行 `node tools/validate.mjs` 确保通过校验
4. 提交 PR

## 许可

MIT
