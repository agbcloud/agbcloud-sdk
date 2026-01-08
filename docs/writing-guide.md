# AGB 文档写作指南（本地）

本指南用于规范 AGB SDK 文档写作方式，目标是让文档 **一致、可读、易检索、易维护**。

> 说明：该文件按约定 **不纳入 git 版本管理**（仅本地使用）。

## 目标

- **先让用户成功**：优先提供可复制运行的最小示例，再补充原理与细节。
- **保持信息架构清晰**：避免重复“唯一事实来源”，减少多处同步维护成本。
- **便于扫描与维护**：结构稳定、标题清晰、示例可运行。

## 新文档应该写在哪里

本仓库文档按 **模块能力页 + 可运行示例 + 自动生成的 API Reference** 组织。新增内容优先放到已有目录下：

- **模块文档（任务/能力/最佳实践/排障）**：放在对应模块目录下（例如 `docs/session/`、`docs/file-system/`、`docs/code-interpreting/`、`docs/browser/`、`docs/context/` 等）
- **Examples（示例）**：`docs/examples/`（可运行的端到端示例，尽量配套 README 指引怎么跑）
- **Quickstart（快速开始）**：`docs/quickstart.md`（新用户第一入口）
- **API Reference（自动生成）**：`docs/api-reference/`（由脚本根据代码注释生成，**不要手写/手改参数表**）

如果你不确定放哪：
- 需要“解释怎么做/什么时候用/注意事项/排障”的，优先放到对应模块目录（例如 `docs/file-system/`）。
- 需要“可直接运行”的，优先放到 `docs/examples/`，并在模块页面里加一个“Examples/Related”入口链接。

## API Reference（自动生成）怎么写好

`docs/api-reference/` 由脚本根据 **代码注释/docstring** 自动生成。API Reference 的准确性取决于代码注释质量，因此开发者必须认真编写注释，务必 **准确、详尽、可维护**。

### 推荐做法

- **为公开 API 写清楚 docstring**：
  - 说明该方法/类解决什么问题、适用场景、边界条件
  - 列出关键参数的语义（不要只写类型名）
  - 解释返回值的含义与常见失败原因
- **包含可复制的最小示例**（如果方法容易误用/步骤多）
- **与实现保持一致**：修改行为/参数/默认值时，必须同步更新注释
- **错误信息要可定位**：返回 `error_message` 时要能指导用户如何排查/修复
- **类型标注齐全**：类型提示是生成与阅读文档的重要信号

## 全局规则

### 以用户任务为起点

建议写作顺序：

1. **你能做什么**（一句话概述）
2. **怎么做**（最小可运行示例 + 必要步骤）
3. **为什么这样做**（原理、边界、注意事项、排障）

### 每个页面至少包含

- **What you’ll do**：1 句话说明本页解决什么问题
- **Prerequisites**：API Key、`image_id`、权限/网络要求等
- **Minimal runnable example**：可直接复制运行的最小示例

### 推荐的标题结构（按需选用）

- Overview
- When to use / When not to use
- Prerequisites
- Quickstart
- Common tasks
- Best practices
- Troubleshooting
- Next steps / Related

### 不要重复 API Reference

- 不要在模块文档里逐条复述所有参数。
- 对参数含义、返回结构等，优先 **链接到** `docs/api-reference/` 的对应页面。

### 单一事实来源（Single Source of Truth）

当新增内容与已有页面重叠时：

- **更新“权威页”**（canonical page）
- 旧页面改成简短说明并指向新位置（必要时做重定向/迁移说明）

### 代码示例规范

- **示例必须可运行**（能复制执行，避免伪代码）
- **创建 session 必须展示清理**（例如 `agb.delete(session)`）
- **展示错误处理**（例如 `if not result.success: ...`）
- **命名保持一致**：推荐 `agb`、`params`、`create_result`、`session`

## 文档模板（建议）

### 模板：模块文档页（`docs/<module>/<topic>.md`）

```markdown
# <标题：清晰描述用户目标>

## What you’ll do
一句话说明本页完成什么。

## Prerequisites
- AGB_API_KEY
- image_id
- 其他依赖/权限

## Quickstart
<最小可运行示例>

## Common tasks
### 场景 A
...

## Best practices
- ...

## Troubleshooting
### 现象
原因与解决方法

## Related
- 链接到 api-reference / 相关模块页面 / examples
```

### 模板：示例（`docs/examples/<module>/...`）

```markdown
# <示例标题>

## 目标
一句话说明示例做什么。

## 完整代码
<可复制运行的完整代码>

## 说明
- 清理逻辑
- 超时与重试
- 成本与注意事项
```

## PR 自检清单

- 文档位置是否合适（guides / examples / api-reference）？
- 是否包含最小可运行示例？
- 是否写清楚 `image_id` 与前置条件？
- 是否展示错误处理与资源清理？
- 是否避免重复 API Reference，并添加了必要链接？

