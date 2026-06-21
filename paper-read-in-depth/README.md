# paper-read-in-depth

深度阅读学术论文，生成结构化中文总结 Markdown 文件。

## 安装

将 `paper-read-in-depth/` 目录复制到 `~/.agents/skills/` 下，或通过 `skills_setup` 脚本添加。

手动安装：
```bash
cp -r /path/to/paper-read-in-depth ~/.agents/skills/
```

## 使用方法

激活 skill 后，向 agent 提供论文来源即可自动执行完整阅读流程。

### 输入格式支持

| 类型 | 示例 |
|------|------|
| arXiv 链接 | `https://arxiv.org/abs/2301.12345` |
| DOI 链接 | `https://doi.org/10.xxxx/xxxxx` |
| 本地 PDF 路径 | `/path/to/paper.pdf` |

### 输出

在 Desktop 生成 `<论文标题缩写>-summary.md` 文件。

## 工作流程

1. **获取论文内容** — 根据输入类型读取/抓取论文
2. **背景研究** — 需要时派生子任务或联网检索背景知识
3. **主线分析** — 提取核心问题、新方法、新结论及核心证据链
4. **技术细节** — 实验方法、辅助证据、理论推导
5. **价值评估** — 进步性、不足、横向对比、同行反响
6. **生成总结** — 输出结构化 Markdown

## 依赖

- `load_skill` 用于加载 `dispatching-parallel-agents` skill（背景研究嵌套阅读）
- `web_fetch` 用于 DOI/arXiv 抓取和互联网检索
# paper-read-in-depth
