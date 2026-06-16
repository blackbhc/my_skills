# Skill 开发指南

本文档说明如何创建、编写和发布 Skill。

---

## 目录

- [什么是 Skill](#什么是-skill)
- [目录结构](#目录结构)
- [YAML Frontmatter 规范](#yaml-frontmatter-规范)
- [SKILL.md 编写规范](#skillmd-编写规范)
- [触发机制设计](#触发机制设计)
- [指令编写原则](#指令编写原则)
- [测试与调试](#测试与调试)
- [发布流程](#发布流程)

---

## 什么是 Skill

Skill 是**可复用的 LLM 指令集**。每个 Skill 是一个独立的 `SKILL.md` 文件，存放在 `<skill-id>/` 目录下。Skill 的 YAML frontmatter 中定义触发词，当用户输入匹配时，Skill 的指令被注入到 Agent 的 system prompt 中。

**Skill 的设计哲学：**

- **单一职责** —— 一个 Skill 只做一件事
- **无副作用** —— 不干扰其他 Skill 的行为
- **可组合** —— 多个 Skill 可以协同工作
- **可发现** —— 通过 YAML frontmatter 被系统自动扫描加载

---

## 目录结构

```text
my_skills/
├── <skill-id>/               # Skill 目录，id 需唯一
│   └── SKILL.md              # ★ 唯一必需文件
├── templates/                # Skill 模板
├── tools/                    # 校验工具
└── docs/                     # 开发文档
```

目录名（`<skill-id>`）必须与 `SKILL.md` 中 YAML frontmatter 的 `name` 字段完全一致。

---

## YAML Frontmatter 规范

**每个 SKILL.md 必须以 YAML frontmatter 开头。** 缺少 frontmatter 的 Skill 无法被系统扫描和加载。

### 格式

```yaml
---
name: <skill-id>                          # 必需。小写字母+数字+连字符，与目录名一致
description: |                            # 必需。多行文本
  <一句话描述 skill 功能>

  Use when: <触发词1, 触发词2, ...>       # ★ 必需。这一行定义触发词，逗号分隔
allowed-tools:                            # 必需。本 Skill 需要使用的工具白名单
  - Read
  - Write
  - Bash
---
```

### 字段说明

| 字段 | 必需 | 说明 | 示例 |
|------|:----:|------|------|
| `name` | ✅ | 唯一标识符。小写字母+数字+连字符，与目录名一致 | `code-review-skill` |
| `description` | ✅ | 第一行：一句话描述。**必须包含 `Use when:` 行**，后跟逗号分隔的触发词 | `Use when: 审查代码, code review, 代码质量` |
| `allowed-tools` | ✅ | 本 Skill 运行时需要的工具列表 | `- Read` `- Bash` `- Grep` |

### 常见错误

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| 没有 `---` 包裹的 YAML 块 | Skill 不被发现 | 文件第一行必须是 `---` |
| `description` 中没有 `Use when:` 行 | 无法匹配触发词 | 显式写 `Use when: xxx, yyy` |
| `name` 与目录名不一致 | 校验失败 | 保持严格一致 |
| `---` 不闭合 | YAML 解析失败 | frontmatter 以第二个 `---` 结尾 |

### 参考

- 模板：[templates/SKILL.template.md](../templates/SKILL.template.md)
- 校验：`node tools/validate.mjs` 自动检查以上错误
- Skill Builder：直接问 Agent「用 skill_builder 帮我创建一个 Skill」，Agent 会自动生成符合规范的 SKILL.md

---

## SKILL.md 编写规范

### 标准结构

```markdown
---
name: <skill-id>
description: |
  ...

  Use when: ...
allowed-tools:
  - Read
---

# Skill: <skill-id>

## Purpose
## Use When
## Inputs
## Workflow
## Outputs
## Limitations
## Examples
## Checklist
```

各章节说明：

| 章节 | 必需 | 说明 |
|------|:----:|------|
| YAML frontmatter | ✅ | 见上方「YAML Frontmatter 规范」 |
| `# Skill:` 标题 | ✅ | 与 name 一致 |
| Purpose | ✅ | 一句话说明用途 |
| Use When | ✅ | 详细触发条件列表 |
| Inputs | ❌ | 输入定义，标注必需/可选 |
| Workflow | ✅ | 分步骤指令 |
| Outputs | ✅ | 输出内容和格式 |
| Limitations | ❌ | 明确不负责什么 |
| Examples | ❌ | 至少 1 个输入→输出示例 |
| Checklist | ❌ | 质量自检清单 |

---

## 触发机制设计

触发词定义在 YAML frontmatter 的 `Use when:` 行中。设计原则：

### 1. 覆盖常见表述

用户可能用不同方式表达同一需求。覆盖中英文常见变体：

```yaml
# 好
Use when: 代码审查, code review, 审查代码, review code, review PR

# 不好（只覆盖了一种）
Use when: code review
```

### 2. 避免过度泛化

不要使用太通用的词，否则 Skill 会被错误激活：

```yaml
# 好（具体）
Use when: 代码审查, code review, review pull request, 审查PR

# 不好（过于宽泛，会匹配所有含「代码」的对话）
Use when: 代码, code
```

### 3. 动词 + 名词组合

优先使用「动词+名词」短语组合，提高精确度：

| 推荐 | 不推荐 |
|------|--------|
| `写测试, write tests` | `测试, test` |
| `重构代码, refactor code` | `重构, refactor` |

---

## 指令编写原则

Workflow 是 Skill 最核心的部分，直接注入 Agent 的 system prompt。遵循以下原则：

### 1. 用祈使句

用直接指令而非描述性语言：

```
✅ "分析代码质量，输出 3 个风险项"
❌ "这个 Skill 会分析代码质量，然后它会输出风险项"
```

### 2. 分步骤编号

复杂行为按步骤编号：

```markdown
1. 读取用户提供的代码或 diff
2. 逐文件分析以下维度：安全性、性能、可维护性、风格
3. 输出优先级排序的问题列表
4. 对每个问题给出修复建议
```

### 3. 明确边界

在 Limitations 章节明确指出什么不负责：

```markdown
## Limitations

- 不要修改用户代码
- 不要执行代码
- 不要在未确认时自动修复
```

### 4. 给出示例

在 Examples 章节用示例说明期望行为：

```markdown
## Examples

### 示例 1
> **用户**：审查这个 PR
> **Agent 输出**：按 P0/P1/P2 列出问题 + 修复建议
```

### 5. 结构化输出模板

定义清晰的输出结构：

```markdown
## Outputs

按以下结构输出：
1. **概览**：总体评价 + 问题数量
2. **问题列表**（按优先级 P0/P1/P2 排序）
3. **亮点**（可选）
```

---

## 测试与调试

### 本地验证

```bash
# 运行校验脚本（扫描所有 Skill）
node tools/validate.mjs

# 指定文件校验
node tools/validate.mjs my-skill/SKILL.md
```

### 测试方法

1. **单元测试** —— 用典型输入触发 Skill，观察 Agent 是否按预期行为
2. **边界测试** —— 用极简输入、极长输入、不相关输入测试 Skill 是否正确激活或不激活
3. **组合测试** —— 当多个 Skill 同时激活时，确认没有冲突
4. **回归测试** —— 修改后重新运行验证，确保旧有行为不受影响

### 调试技巧

- 如果 Skill 未激活，检查 `Use when:` 是否覆盖了用户的表达方式
- 如果 Skill 从未被激活，检查 YAML frontmatter 是否存在、`---` 是否正确闭合
- 如果 Agent 行为异常，检查 Workflow 是否包含矛盾指令

---

## 发布流程

1. **开发** —— 从模板复制，或让 Agent 用 skill_builder 生成
2. **校验** —— `node tools/validate.mjs` 通过
3. **自测** —— 本地验证 Skill 激活和行为
4. **提交 PR** —— 提交到本仓库
5. **发布** —— 合并后发布 Release

### 版本管理

- 初始版本设为 `1.0.0`
- 重大行为变更 → 主版本号增加
- 新增功能/触发条件 → 次版本号增加
- 缺陷修复/文案优化 → 补丁版本号增加

---

## 更多

- [Skill 模板](../templates/SKILL.template.md)
- [校验工具](../tools/validate.mjs)
- [Skill Builder](../skill_builder/SKILL.md)
