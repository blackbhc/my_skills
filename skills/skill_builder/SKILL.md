# Skill Builder（Skill开发助手）

## Purpose

帮助 Agent 设计、开发、重构、优化和维护其他 Skill。

本 Skill 专门用于构建 Skill，而不是直接解决业务问题。其目标是帮助 Agent 生成高质量、可维护、可复用、可发现的 Skill。

---

## Use When

满足以下任意条件时使用：

- 用户要求开发新的 Skill
- 用户要求优化现有 Skill
- 用户要求设计 Agent 工作流
- 用户要求编写 Skill README
- 用户要求制定 Skill 规范
- 用户要求构建 Agent 能力库
- 用户要求将 Prompt 转换为 Skill
- 用户要求建立可复用解决方案

典型触发词：

- 创建 skill
- 开发 skill
- 优化 skill
- skill设计
- agent能力
- workflow设计
- prompt工程
- prompt转skill
- 构建工具链
- 自动化流程

---

## Core Objective

开发出的 Skill 必须满足：

- 用途清晰
- 触发条件明确
- 输出结果确定
- 边界定义清楚
- 示例充分
- 易于维护
- 易于被 Agent 自动发现和调用

---

# Skill Design Principles

## 1. 单一职责原则

一个 Skill 只解决一个明确问题。

推荐：

- paper-review
- latex-polish
- referee-response
- git-workflow

不推荐：

- research-helper
- academic-assistant
- all-in-one-agent

如果一个 Skill 需要用“以及”、“同时”、“顺便”等词描述其职责，则通常说明职责过多。

---

## 2. 先定义问题，再定义方案

错误方式：

> 先设计 Prompt。

正确方式：

先明确：

- 用户遇到了什么问题
- Skill 解决什么问题
- 为什么需要 Skill

然后再设计工作流。

---

## 3. 明确触发条件

必须回答：

> Agent 在什么情况下应该使用该 Skill？

示例：

错误：

> 用于帮助编程。

正确：

> 当用户要求分析 Python 项目结构、生成重构方案或解释代码库时使用。

---

## 4. 明确边界

必须说明：

### Skill负责什么

例如：

- Latex语法润色
- 学术表达优化

### Skill不负责什么

例如：

- 科学结论验证
- 数据真实性判断

---

## 5. 明确输出

Skill 必须产生确定结果。

示例：

输入：

> 优化论文摘要

输出：

- 问题分析
- 修改建议
- 修改后版本

而不是：

> 提供帮助

---

## 6. 优先流程化

不要依赖模型临场发挥。

优先提供：

- 步骤
- 检查表
- 模板
- 示例

而不是：

> 根据情况决定。

---

# Standard Skill Structure

推荐目录结构：

```text
skill-name/
├── README.md
├── examples/
├── templates/
└── references/
```

README 应包含：

```markdown
# Skill Name

## Purpose

## Use When

## Inputs

## Workflow

## Outputs

## Limitations

## Examples

## Checklist
```

---

# Skill Development Workflow

开发 Skill 时按照以下流程执行。

---

## Phase 1：需求分析

回答以下问题：

1. Skill解决什么问题？
2. 谁会使用？
3. 使用频率高吗？
4. 是否值得沉淀为 Skill？
5. 与已有 Skill 有何区别？

输出：

```text
目标
用户
场景
约束
边界
```

---

## Phase 2：职责定义

明确：

```text
负责什么
不负责什么
```

示例：

负责：

- Latex润色

不负责：

- 科学正确性审查

---

## Phase 3：触发条件设计

设计：

```text
何时调用
何时不调用
```

示例：

调用：

- 用户要求学术英语润色

不调用：

- 用户询问天体物理知识

---

## Phase 4：输入设计

定义 Skill 所需输入：

```text
必需输入
可选输入
默认值
```

示例：

```text
论文内容（必需）
目标期刊（可选）
语言风格（可选）
```

---

## Phase 5：工作流设计

将任务拆解为稳定步骤。

推荐：

```text
输入分析
↓
信息收集
↓
执行
↓
验证
↓
输出
```

每一步都应可独立理解和执行。

---

## Phase 6：输出设计

定义：

```text
必须输出什么
可选输出什么
```

示例：

```text
问题分析
修改建议
最终结果
```

---

## Phase 7：示例设计

至少提供：

```text
简单案例
真实案例
边界案例
```

示例应覆盖：

- 正常情况
- 极端情况
- 错误输入

---

## Phase 8：质量检查

确认：

- 目标明确
- 触发条件明确
- 输入明确
- 输出明确
- 边界明确
- 示例充分
- 无明显歧义

---

# Long Task Planning Framework

对于复杂 Skill 开发任务，必须采用规划框架。

禁止：

```text
直接生成最终Skill
```

推荐：

---

## Step 1：目标定义

输出：

```text
最终目标
成功标准
约束条件
风险因素
```

---

## Step 2：任务拆分

拆分为多个模块：

```text
模块A
模块B
模块C
...
```

要求：

- 模块之间低耦合
- 可独立验证
- 可独立迭代

---

## Step 3：执行计划

为每个模块制定：

```text
目标
输入
输出
完成标准
```

---

## Step 4：阶段执行

一次只完成一个阶段。

示例：

```text
Phase 1
需求分析
```

完成后再进入：

```text
Phase 2
架构设计
```

避免在信息不足时提前实施后续阶段。

---

## Step 5：阶段验证

每阶段结束后检查：

```text
目标是否达成
结果是否正确
是否产生新问题
是否需要调整计划
```

---

## Step 6：最终整合

输出：

```text
最终Skill
使用说明
示例
限制说明
维护建议
```

---

# Skill Description Template

开发任何 Skill 时，优先生成以下内容。

```markdown
# Skill Name

## Purpose

一句话说明用途。

## Use When

列出触发条件。

## Inputs

所需输入。

## Workflow

步骤1

步骤2

步骤3

## Outputs

输出内容。

## Limitations

不负责什么。

## Examples

示例1

示例2

## Checklist

质量检查项。
```

---

# Good Example

## Purpose

帮助润色天体物理论文，使其符合 ApJ 风格。

## Use When

用户要求：

- 学术英语润色
- ApJ风格修改
- referee回复优化

## Outputs

- 修改后文本
- 修改原因
- 语言问题清单

---

# Bad Example

## Purpose

帮助科研。

问题：

- 范围过大
- 无触发条件
- 无边界说明
- 无输出规范

---

# Final Rules

开发 Skill 时始终遵循：

1. 先定义问题，再定义 Prompt。
2. 先定义触发条件，再定义实现方式。
3. 先定义输出，再定义工作流。
4. 长任务先规划，再执行。
5. 优先小而专，而非大而全。
6. Skill 应能脱离当前上下文独立使用。
7. Skill 应能被其他 Agent 快速理解和调用。
8. Skill 应包含示例，而非仅包含规则。
9. Skill 应优先复用成熟模式，而非重复发明流程。
10. 如果无法一句话说明用途，则说明 Skill 设计仍不够清晰。
