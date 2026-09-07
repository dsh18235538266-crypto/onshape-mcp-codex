# onshape-mcp-codex

> OpenAI Codex 版 Onshape CAD MCP server —— 让 Codex 对话驱动真实的参数化 CAD

本仓库是 [jarvis-onshape-mcp](https://github.com/ReshefElisha/jarvis-onshape-mcp)（★168，MIT）的 **Codex 适配 fork**。复用其全部 ~69 个 MCP 工具与 CAD 方法论，替换 Claude 专属接入层为 Codex 兼容形式（MCP stdio + server instructions + Codex skills）。

## 与上游的区别

| | jarvis-onshape-mcp（上游） | onshape-mcp-codex（本仓库） |
|---|---|---|
| 目标客户端 | Claude Code（`.claude-plugin`） | **OpenAI Codex**（stdio MCP） |
| 接入方式 | `/plugin install` | `codex mcp add` 或 `~/.codex/config.toml` |
| MCP server 内核 | `onshape_mcp/`（69 工具） | ✅ 同源保留 |
| 方法论注入 | SKILL.md（Claude 加载） | **MCP instructions 字段**（Codex 读前 512 字符）+ Codex skills |
| 依赖 | 含 `anthropic` / `claude-agent-sdk` | ✅ 已去除，仅 mcp/httpx/pydantic 等 |

## 它能干什么

Codex 获得 69 个工具，可驱动真实 Onshape CAD：

- **Document**：创建/查找文档、Part Studio、装配
- **Sketch**：多实体草图 + 14 种约束（坐标优先 / 约束优先双模式）
- **Feature**：拉伸/旋转/加厚/倒角/圆角/抽壳/布尔/阵列/偏置面
- **Assembly**：4 种配合（固定/滑块/旋转/圆柱）+ 干涉检查 + 实例对齐
- **Parametric**：Variable Studio 参数化迭代（改一个变量驱动整条特征链）
- **FeatureScript**：逃逸舱口——Codex 直接写 FeatureScript 自定义特征（螺纹/扫掠/放样）
- **Vision**：多视图 PNG 渲染、crop 放大、参考图对比、工程图 OCR
- **Export**：STL / STEP / GLTF

**关键设计（继承自 jarvis 的 truth-telling）**：每个变更工具返回 `{ok, status, feature_id, changes?, hints?}`，特征失败带修复提示，Codex 不会在静默失败上继续堆特征。

## 快速开始

### 1. 注册 Onshape API Key

在 [dev-portal.onshape.com](https://dev-portal.onshape.com/) 创建 OAuth/API 密钥对，得到 `ONSHAPE_API_KEY` + `ONSHAPE_API_SECRET`。

### 2. 安装

```bash
pip install onshape-mcp-codex
# 或本地开发
git clone https://github.com/yourname/onshape-mcp-codex.git
cd onshape-mcp-codex
pip install -e .
```

### 3. 接入 Codex

```bash
codex mcp add onshape \
  --env ONSHAPE_API_KEY=你的Key \
  --env ONSHAPE_API_SECRET=你的Secret \
  -- onshape-mcp-codex
```

或手动编辑 `~/.codex/config.toml`：

```toml
[mcp_servers.onshape]
command = "onshape-mcp-codex"
env = {
  ONSHAPE_API_KEY = "你的Key",
  ONSHAPE_API_SECRET = "你的Secret",
}
```

### 4. 验证

```
codex mcp list        # 应看到 onshape 及 69 个工具
```

新开 Codex 会话，试试：

> "创建一个新的 Onshape 文档，加一个 Part Studio，做一个 60×40×8 的安装板，四角 6mm 内打 Ø4 孔"

### 5. 安装方法论 skills（推荐）

仓库 `skills/` 提供两个 Codex skill，完整承载 CAD 方法论：

```bash
# CAD 构建协议（render-first / entity-first / 迭代纪律 / 陷阱表）
mkdir -p ~/.codex/skills && cp -r skills/onshape ~/.codex/skills/
# 视觉分解（参考图 → 结构化特征树，先描述后建模）
cp -r skills/vision-decompose ~/.codex/skills/
```

安装后 Codex 遇到 CAD 任务会自动匹配加载；参考图建模时显式要求走 vision-decompose 流程。

## MCP instructions（自动注入）

server 启动时通过 MCP `instructions` 字段注入 6.3KB 工具索引 + 协议（Codex 读取该字段并用于整个会话）。**前 512 字符自包含**关键约束：mm 单位、`describe_part_studio` 验证循环、面/边选取前必须 `list_entities`。

## 已知限制

与上游一致：
- Onshape 平台无 section-view REST 端点（仅 UI Shift+X）
- `create_fillet` 的 `variableCenter` 遇 Onshape 侧 phantom-reference bug（裸半径正常）
- 图像理解仍是墙：Codex 从工程图自主建模质量低于"人类描述规格 → 建模"（见 RESEARCH.md 的 2×2 基准）

## 致谢

- [ReshefElisha/jarvis-onshape-mcp](https://github.com/ReshefElisha/jarvis-onshape-mcp) — 内核与方法论（MIT）
- [hedless/onshape-mcp](https://github.com/hedless/onshape-mcp) — 上游的 REST client 基础

## License

MIT
