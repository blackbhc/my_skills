# LLM Skill 开发仓库

一套面向大语言模型（LLM）应用的 Skill 开发框架与技能合集。

---

## 目录

```
my_skills/
├── skills/           # ★ Skill 技能定义
│   └── tokens-auto-specialization/
├── templates/        # Skill 模板
├── tools/            # 校验与开发工具
└── docs/             # 开发指南
```

## 已有 Skill

| Skill | 描述 |
|-------|------|
| [tokens-auto-specialization](skills/tokens-auto-specialization/SKILL.md) | 提示词自动专业化——用户给出场景+用途，自动补齐角色/规则/格式，输出精简版+顶配版，跨模型适配 |

## 快速开始

```bash
# 1. 克隆仓库
git clone <repo-url> my_skills
cd my_skills

# 2. 校验已安装的 skill
node tools/validate.mjs
```

### 创建新 Skill

```bash
# 复制模板
cp templates/SKILL.template.md skills/<your-skill-name>/SKILL.md

# 编辑后校验
node tools/validate.mjs
```

参见 [docs/skill-development.md](docs/skill-development.md) 获取完整开发指南。

## 使用 Skill

每个 Skill 可通过以下方式使用：

```bash
# 1. 将 skill 目录复制/链接到你的项目中使用
cp -r skills/<skill-id> /your-project/skills/<skill-id>

# 2. 在对话中通过 @skill-id 或相关关键词激活 Skill
```

详见 [docs/skill-development.md](docs/skill-development.md) 获取完整使用指南。

## 贡献

欢迎提交新的 Skill！请遵循以下流程：

1. 从 `templates/SKILL.template.md` 复制模板
2. 按 `docs/skill-development.md` 中的规范填写
3. 运行 `node tools/validate.mjs` 确保通过校验
4. 提交 PR

## 许可

MIT
