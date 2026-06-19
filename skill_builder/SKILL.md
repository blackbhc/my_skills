---
name: skill_builder
description: |
  Skill 开发助手——指导 Agent 设计、开发、重构、优化和维护其他 Skill。确保产出的 Skill 格式规范（含 YAML frontmatter）、可被系统自动发现和加载。

  Use when: 创建skill, 开发skill, 优化skill, skill设计, 构建skill, 重建skill, 写skill, 设计工作流, agent能力, 工作流设计, prompt转skill, 构建工具链, 自动化流程, skill格式, skill规范, 制作skill, create skill, develop skill, build skill, design skill, optimize skill, skill development, 改写skill
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - WebFetch
---

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
- **格式规范：必须包含 YAML frontmatter（见下方「YAML Frontmatter 规范」）**

---

# YAML Frontmatter 规范（★ 硬性要求）

**每一个 Skill 的 SKILL.md 文件必须以 YAML frontmatter 开头。** 缺少 frontmatter 的 Skill 无法被系统扫描和加载，等于不存在。

## 格式

```yaml
---
name: <skill-id>                          # 必需。小写字母、数字、连字符。必须与目录名一致
description: |                            # 必需。多行描述
  <一句话描述 skill 功能>

  Use when: <触发词1, 触发词2, ...>       # ★ 必需。写在这一行，逗号分隔
allowed-tools:                            # 必需。本 skill 需要使用的工具列表
  - Read
  - Write
  - Bash
---
```

## 各字段说明

| 字段 | 必需 | 格式 | 示例 |
|------|:----:|------|------|
| `name` | ✅ | 小写字母+数字+连字符，与目录名一致 | `code-review-skill` |
| `description` | ✅ | 多行文本。第一行是一句话描述。**必须包含一行 `Use when:`** 后跟逗号分隔的触发词 | `Use when: 审查代码, code review, 代码质量` |
| `allowed-tools` | ✅ | YAML 列表，声明本 skill 运行时需要的工具 | `- Read` `- Bash` `- Grep` |

## 常见错误

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| 没有 `---` 包裹的 YAML 块 | Skill 不被发现 | 文件第一行必须是 `---` |
| `description` 中没有 `Use when:` 行 | 无法匹配触发词 | 在 description 中显式写 `Use when: xxx, yyy` |
| `name` 与目录名不一致 | 校验失败 | 目录名和 name 字段保持严格一致 |
| `---` 只出现在开头缺了结尾 | YAML 解析失败 | frontmatter 必须以第二个 `---` 闭合 |

## 在校验环节确认

Phase 8（质量检查）中，你必须确认产出的 SKILL.md：

- [ ] 文件前 3 行是否以 `---` 开头？
- [ ] `name` 是否与目录名一致？
- [ ] `description` 中是否包含 `Use when:` 行？
- [ ] `allowed-tools` 是否声明了 skill 需要的工具？
- [ ] frontmatter 是否被第二个 `---` 正确闭合？

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

如果一个 Skill 需要用「以及」「同时」「顺便」等词描述其职责，则通常说明职责过多。

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
├── SKILL.md          # ★ 唯一必需文件（含 YAML frontmatter）
├── README.md         # 可选：人类阅读的说明文档
├── examples/         # 可选：示例
├── templates/        # 可选：模板
└── references/       # 可选：参考资料
```

**SKILL.md 必须包含的结构：**

```markdown
---
name: <skill-id>
description: |
  <一句话描述>

  Use when: <触发词列表>
allowed-tools:
  - Read
  - Write
---

# Skill: <skill-id>

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

# Skill Development Workflow

开发 Skill 时按照以下流程执行。

---

## Phase 1：需求分析与意图捕获

### 1.1 采访用户

通过与用户对话，澄清以下 4 个核心问题：

1. **目标**：这个 Skill 应该让 Agent 做什么？
2. **触发时机**：用户说什么/什么上下文时应该激活？收集具体短语和表述变体
3. **输出格式**：Agent 应用该 Skill 后应该产生什么？
4. **测试验证**：是否需要测试用例来验证 Skill 生效？（客观可验证的输出如文件转换/代码生成需要；主观输出如风格写作通常不需要）

### 1.2 主动调研

- 主动追问边缘情况：输入/输出格式、示例文件、成功标准、依赖项
- 检查是否有可用 MCP（文档搜索、类似 Skill 查找、最佳实践）
- 如果当前对话历史中已有用户的工作流，从中提取工具的调用顺序、用户纠正、输入输出格式

### 1.3 确认后再推进

用户确认上述内容后，再进入 Phase 2。

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

- [ ] 目标明确
- [ ] 触发条件明确
- [ ] 输入明确
- [ ] 输出明确
- [ ] 边界明确
- [ ] 示例充分
- [ ] 无明显歧义
- [ ] 如果是行为塑造型 Skill：是否用 TDD 流程（RED→GREEN→REFACTOR）开发？
- [ ] 是否已在「无 Skill」状态下验证 Agent 会失败？（即确认有创建此 Skill 的必要）

---

# YAML Frontmatter 生成流程（★ 新增）

在产出任何 Skill 时，你必须按以下步骤生成 YAML frontmatter：

## Step 1：确定 name

`name` 必须等于 Skill 所在目录名。格式：小写字母 + 数字 + 连字符。

```
正确：code-review-skill
正确：tokens-auto-specialization
错误：Code Review Skill
错误：code_review_skill
```

## Step 2：撰写 description

第一行：一句话描述。
第二行：空行。
第三行：`Use when: <触发词1>, <触发词2>, ...`

触发词来源：Phase 3 中设计的调用条件，提取关键词，逗号分隔。

```
Use when: 审查代码, code review, 代码质量, review PR, 检查代码
```

触发词设计原则：
- 覆盖中英文常见变体
- 优先「动词+名词」组合
- 避免过度泛化（如「代码」「测试」等单一名词）

## Step 3：声明 allowed-tools

列出本 Skill 运行时需要调用的工具名称：

```yaml
allowed-tools:
  - Read
  - Bash
  - Grep
```

如果不确定，至少包含 `Read`。

## Step 4：组装并校验

将以上三步组装为完整的 YAML frontmatter，用 `---` 包裹，放在 SKILL.md 第一行。

校验清单：
- [ ] `name` 与目录名一致？
- [ ] `description` 包含 `Use when:` 行？
- [ ] 第二个 `---` 正确闭合？

---

# TDD for Skills（★ 测试驱动的 Skill 开发方法论）

这是对上方传统工作流的**补充增强**。并非所有 Skill 都需要完整 TDD 流程——**行为塑造型（discipline）Skill 必须用 TDD**，纯参考/信息型 Skill 可用传统流程。

**核心原则：** 如果你没有在「没有 Skill」的情况下先看 Agent 失败，你就不知道 Skill 是否真的教会了正确行为。

## RED 阶段：先看到失败

在写任何 Skill 代码之前，先证明现在的 Agent 没有你的 Skill 会做错。

### 1. 构造压力场景

设计 3 个以上测试场景，每个场景叠加 2–3 个压力源：

```text
# 示例：为「代码审查 Skill」构造压力场景
场景1: PR 包含安全漏洞 + 代码风格不一致 + 性能问题
场景2: 大 diff（500+行）+ 无 PR 描述 + deadline 紧迫
场景3: 多人协作 + 分支冲突 + 测试失败
```

### 2. 无 Skill 基线测试

在没有本 Skill 的情况下运行压力场景，**逐字记录** Agent 的失败模式：

- 忽略了什么？
- 错误地关注了什么？
- 做了哪些不合理的事？
- 用哪些理由为自己辩护？

**关键技巧：** 将 WITH skill 和 WITHOUT skill 的测试**在同一轮次同时启动**，不要串行（先测 with-skill 再补 baseline 会因上下文扰动影响公平性）。

### 2.1 创建测试基础设施

在编写 Skill 正文之前，创建测试目录结构：

```text
<skill-name>-workspace/
├── evals/
│   └── evals.json         # 测试用例（prompt + 预期输出 + 断言）
├── iteration-1/
│   ├── eval-<name>/
│   │   ├── with_skill/    # 带 Skill 的输出
│   │   └── without_skill/ # 无 Skill 的 baseline
│   └── ...
└── timing.json            # 每次运行的 tokens + duration 记录
```

每个测试用例用描述性命名（如 `eval-security-review` 而非 `eval-0`）。

### 2.2 捕获时序数据

每个测试子任务完成后，立即保存：

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332
}
```

这些数据随任务通知到达，不会持久保留，必须即时处理。

### 3. 识别失败模式

从基线测试中归纳出 Agent 的**常见失败模式**：

| 失败模式 | 表现 | 根因 |
|----------|------|------|
| 遗忘安全 | 未检查 SQL 注入、XSS | 安全审查不被视为优先事项 |
| 风格摇摆 | 同一报告内混用多种风格 | 缺乏风格约定基准 |
| 省略证据 | 说「可能有性能问题」但不给数据 | 缺乏量化检查要求 |

---

## GREEN 阶段：写出最小 Skill

### 1. 针对性编写

只修复 RED 阶段发现的具体失败，不要提前防所有可能问题。

```markdown
## Workflow
1. 按安全→性能→可维护性→风格逐文件检查
2. 每个问题必须标注：优先级( P0/P1/P2 )、文件+行号、风险说明、修复建议
...
```

### 2. 逐条验证

每写一条规则，跑一次测试确认这条规则确实改变了 Agent 行为。

### 3. 形式匹配失败类型

| 失败类型 | 适用引导形式 |
|----------|-------------|
| Agent 忽略了某类问题 | 硬性步骤（必须检查 X） |
| Agent 做了错误判断 | 判断标准/阈值定义 |
| Agent 输出格式混乱 | 输出 Schema + 示例 |
| Agent 为自己找借口 | 反例 + 禁止条款 |
| Agent 过早优化 | 优先级排序规定 |

### 4. 微调措辞（行为塑造型 Skill）

对于需要改变 Agent 行为的措辞，在同一压力场景下对比 5 次以上：
- **对照组**：不加本规则的 baseline
- **实验组**：加本规则后的版本

**每一条被标记为匹配的输出都必须人工核验。**

---

## REFACTOR 阶段：封堵漏洞

### 1. 寻找新借口

运行带 Skill 的测试，记录 Agent **仍然犯错时的新借口**：

| Agent 借口 | 所需对策 |
|-----------|---------|
| "安全方面我不专业" | 加约束：「你必须假设自己是安全专家」 |
| "性能问题不在 PR 范围内" | 加约束：「性能是每轮审查必须项」 |
| "这是风格偏好，不影响功能" | 加约束：「风格一致性是质量维度之一」 |

### 2. 构建 Rationalization Table

将全部测试轮次中 Agent 的借口汇总为一张对照表，放入 Skill 的 Examples 或 Checklist 中。

### 3. 反复迭代

重复 RED→GREEN→REFACTOR 直到所有压力场景通过。

---

## Skill Creation Checklist（TDD 版）

**RED Phase - Write Failing Test:**
- [ ] 创建 3+ 压力场景（行为塑造型 Skill 必须）
- [ ] 无 Skill 运行 baseline —— 逐字记录 Agent 失败
- [ ] 归纳失败模式

**GREEN Phase - Write Minimal Skill:**
- [ ] 只针对 baseline 失败模式编写，不提前防御
- [ ] 每条规则对应一个已观察到的失败模式
- [ ] 引导形式匹配失败类型（见上方对照表）
- [ ] 微调措辞（行为塑造型：5+ 轮对比测试）
- [ ] 运行测试 —— Agent 行为已经改善？

**REFACTOR Phase - Close Loopholes:**
- [ ] 查找 Agent 的新借口/新失败模式
- [ ] 构建 Rationalization Table
- [ ] 增加反例和禁止条款
- [ ] 重新测试直到通过

**Quality Checks:**
- [ ] 一个有代表性的好示例（不要多语言稀释）
- [ ] 简单决策流程（用小型流程图，仅当决策不直观时）
- [ ] 常见错误章节
- [ ] 快速参考表
- [ ] 无叙事性故事（不要「在 session 2025-10-03 我们发现…」）

---

# Iteration & Feedback Loop（★ 迭代反馈循环）

这是 TDD 流程完成一轮后的**增强持续改进循环**。

## 定量评估

### 断言编写

在测试运行期间，为每个测试用例编写可客观验证的断言：

```json
{
  "eval_id": 0,
  "eval_name": "security-review",
  "prompt": "审查这个 PR 是否存在安全问题",
  "assertions": [
    {
      "text": "至少识别 1 个安全风险",
      "passed": false,
      "evidence": ""
    },
    {
      "text": "每个风险标注优先级",
      "passed": false,
      "evidence": ""
    }
  ]
}
```

**断言设计原则：**
- 每个断言有描述性名称（在 benchmark 中阅读友好）
- 可客观验证（文件存在/格式正确/包含特定内容）
- 主观质量（写作风格/设计质量）交给人的定性评估

### 评分与聚合

所有测试运行完成后：

1. 逐条评分每个断言（人工或脚本）
2. 聚合为 benchmark 报告：通过率、平均耗时、token 用量
3. 比较 with-skill vs without-skill 的差异

## 反馈驱动迭代

### 1. 展示结果

将测试结果以对比方式呈现（with-skill vs without-skill），让用户逐条审阅。

### 2. 收集反馈

记录用户的每条反馈：

| 场景 | 用户反馈 | 所需改进 |
|------|----------|----------|
| eval-security-review | "漏掉了 SQL 注入检查" | 增加安全检查步骤 |
| eval-performance | "耗时太长" | 简化输出格式 |

### 3. 改进 Skill

根据反馈修改 Skill 后，进入下一轮迭代：
1. 增量版本号（iteration-2/、iteration-3/……）
2. 重新运行所有测试用例（含 baseline）
3. 再次展示对比结果，直到用户满意

### 4. 停止条件

当满足以下任一条件时停止迭代：
- 用户明确表示满意
- 所有反馈为空（一切正常）
- 连续两轮无明显改进

---

# 进阶：结构优化模式

## 渐进式信息披露（Progressive Disclosure）

Skill 内容按三层加载：

```
1. Metadata（name + description） → 始终在上下文（~100 词）
2. SKILL.md 正文                → Skill 激活时加载（<500 行）
3. Bundled resources            → 按需加载（无限，脚本无需加载即可执行）
```

**当 SKILL.md 接近 500 行时：** 增加层级结构，用清晰指引引导 Agent 去读哪个子文件。

**领域组织：** 当 Skill 支持多个框架/平台时，按变体组织：

```text
cloud-deploy/
├── SKILL.md (工作流 + 选择逻辑)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

Agent 只读相关的变体文件，不加载全部。

## 打包重复工作

阅读测试运行日志，注意是否所有子任务都独立写了相同的辅助脚本。如果 3 个测试用例都各自写了一个 `create_report.py`，说明 Skill 应该**内置这个脚本**：

```text
your-skill/
├── SKILL.md     # 使用方法
└── scripts/
    └── create_report.py  # Agent 直接调用，不再重复发明
```

## 描述优化（Description Optimization）

创建 20 个触发评估查询——一半应该触发（should-trigger），一半不应该触发（should-not-trigger）。

**设计原则：**
- should-trigger：同一意图的不同表述（正式/口语/缩写）；用户不显式命名文件类型但明显需要的；边缘用例
- should-not-trigger：**近义词误触**——关键词匹配了但实际需要不同工具的场景（最有价值）
- 不要用明显不相关的（"写个斐波那契"对 PDF Skill 无效）

用这些查询评估 description 的触发准确率，迭代优化。每次评估跑 3 次取稳定结果。

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
最终Skill（含 YAML frontmatter）
使用说明
示例
限制说明
维护建议
```

---

# Skill Description Template

开发任何 Skill 时，优先生成以下内容。

```markdown
---
name: <skill-id>
description: |
  <一句话描述>

  Use when: <触发词1, 触发词2, ...>
allowed-tools:
  - Read
  - Write
---

# Skill: <skill-id>

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

```markdown
---
name: paper-polish
description: |
  帮助润色天体物理论文，使其符合 ApJ 风格。

  Use when: 学术英语润色, ApJ风格修改, 论文润色, referee回复优化, 学术写作
allowed-tools:
  - Read
  - Write
---

# Skill: paper-polish
...
```

---

# Bad Example

```markdown
# Skill: research-helper
...
```

问题：

- **缺少 YAML frontmatter** —— 系统无法发现此 Skill
- 范围过大（「帮助科研」）
- 无触发条件
- 无边界说明
- 无输出规范

---

# Final Rules

开发 Skill 时始终遵循：

1. **行为塑造型 Skill 必须先 RED（无 Skill → 看到失败）→ GREEN（写最小 Skill）→ REFACTOR（封堵漏洞）。**
2. 先定义问题，再定义 Prompt。
3. 先定义触发条件，再定义实现方式。
4. 先定义输出，再定义工作流。
5. 长任务先规划，再执行。
6. 优先小而专，而非大而全。
7. Skill 应能脱离当前上下文独立使用。
8. Skill 应能被其他 Agent 快速理解和调用。
9. Skill 应包含示例，而非仅包含规则。
10. Skill 应优先复用成熟模式，而非重复发明流程。
11. 如果无法一句话说明用途，则说明 Skill 设计仍不够清晰。
12. **★ 每个 Skill 的 SKILL.md 必须以 YAML frontmatter（`---` 包裹的 name/description/allowed-tools）开头，否则系统无法发现和加载。**
13. **★ 不要在 Skill 中写叙事性故事（「在 session X 我们发现…」），用失败模式 + 对策结构替代。**
