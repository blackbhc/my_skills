# Skill 开发指南

本文档说明如何创建、编写和发布 LLM Skill。

---

## 目录

- [什么是 Skill](#什么是-skill)
- [目录结构](#目录结构)
- [SKILL.md 编写规范](#skillmd-编写规范)
- [触发机制设计](#触发机制设计)
- [指令编写原则](#指令编写原则)
- [测试与调试](#测试与调试)
- [发布流程](#发布流程)

---

## 什么是 Skill

Skill 是**可复用的 LLM 指令集**。每个 Skill 是一个独立的 `SKILL.md` 文件，存放在 `skills/<skill-id>/` 目录下。当用户输入匹配 Skill 定义的触发器时，Skill 的指令可被注入到 LLM 的 system prompt 中，使模型表现出特定领域的专业能力。

**Skill 的设计哲学：**
- **单一职责** —— 一个 Skill 只做一件事
- **无副作用** —— 不干扰其他 Skill 的行为
- **可组合** —— 多个 Skill 可以协同工作

---

## 目录结构

```
skills/
├── <skill-id>/                # 技能目录，id 需全局唯一
│   └── SKILL.md               # 技能定义文件（必需）
└── <another-skill>/
    └── SKILL.md
```

目录名（`<skill-id>`）必须与 `SKILL.md` 中的 `id` 字段完全一致。

---

## SKILL.md 编写规范

### 必需结构

```markdown
# Skill: <skill-id>

## Metadata
<!-- 元数据区：给系统读取 -->

## Context
<!-- 上下文：给人类开发者阅读，说明适用场景 -->

## Instructions
<!-- 指令区：★ 核心内容，会注入 AI system prompt -->
```

### 元数据字段

| 字段 | 必需 | 描述 | 示例 |
|------|------|------|------|
| `id` | ✅ | 唯一标识符。小写字母、数字、连字符。必须与目录名一致 | `code-review-skill` |
| `description` | ✅ | 一句话描述。同时给用户和 LLM 阅读 | 自动审查代码质量，检测潜在 bug、安全风险和风格问题 |
| `triggers` | ✅ | 逗号分隔的触发词/短语。建议含中英文变体 | `code review, 代码审查, review code, cr` |
| `name` | ❌ | 中文显示名称 | 代码审查 |
| `version` | ❌ | semver 版本号 | `1.0.0` |
| `author` | ❌ | 作者标识 | `@username` |

### 模板

参考 [templates/SKILL.template.md](../templates/SKILL.template.md) 开始创建新的 Skill。

---

## 触发机制设计

`triggers` 字段定义了 Skill 的激活条件。设计原则：

### 1. 覆盖常见表述

用户可能用不同方式表达同一需求。覆盖中英文常见变体：

```yaml
# 好
triggers: `代码审查, code review, 审查代码, review code, code review request, cr`

# 不好（只覆盖了一种）
triggers: `code review`
```

### 2. 避免过度泛化

不要使用太通用的词，否则 Skill 会被错误激活：

```yaml
# 好（具体）
triggers: `代码审查, code review, review pull request, 审查PR`

# 不好（过于宽泛）
triggers: `代码, code`
```

### 3. 动词 + 名词组合

优先使用「动词+名词」短语组合，提高精确度：

| 推荐 | 不推荐 |
|------|--------|
| `写测试, write tests` | `测试, test` |
| `重构代码, refactor code` | `重构, refactor` |

---

## 指令编写原则

`Instructions` 是 Skill 最核心的部分，直接注入 AI 的 system prompt。遵循以下原则：

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

明确指出什么该做、什么不该做：

```markdown
### 该做的
- 检查常见安全漏洞（XSS、CSRF、SQL注入）
- 检查代码风格一致性

### 不该做的
- 不要修改用户代码
- 不要执行代码
- 不要在未确认时自动修复
```

### 4. 给出正例/反例

用示例说明期望行为：

```markdown
### 正确的输出格式
> ❌ 不好的：这段代码效率可能不高
> ✅ 好的：性能风险（P2）— 第42行使用了 O(n²) 算法，建议替换为 O(n log n) 的 Map 方案
```

### 5. 结构化输出模板

定义清晰的输出结构：

```markdown
### 输出格式
按以下结构输出：
1. **概览**：总体评价 + 问题数量
2. **问题列表**（按优先级排序）：
   - 优先级（P0/P1/P2）
   - 文件路径 + 行号
   - 问题描述
   - 修复建议
3. **亮点**（可选）：做得好的部分
```

---

## 测试与调试

### 本地验证

```bash
# 运行校验脚本
node tools/validate.mjs

# 指定文件校验
node tools/validate.mjs skills/my-skill/SKILL.md
```

### 测试方法

1. **单元测试** —— 触发 Skill，观察 LLM 是否按预期行为
2. **边界测试** —— 用极简输入、极长输入、不相关输入测试 Skill 是否正确激活或不激活
3. **组合测试** —— 当多个 Skill 同时激活时，确认没有冲突
4. **回归测试** —— 修改后重新运行验证，确保旧有行为不受影响

### 调试技巧

- 观察 LLM 的完整 system prompt，确认 Skill 的指令是否被正确注入
- 如果 Skill 未激活，检查 `triggers` 是否覆盖了用户的表达方式
- 如果 LLM 行为异常，检查 `Instructions` 是否包含矛盾指令

---

## 发布流程

1. **开发** —— 从模板复制，按本指南编写
2. **校验** —— `node tools/validate.mjs` 通过
3. **自测** —— 本地验证
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
- [README](../README.md)
