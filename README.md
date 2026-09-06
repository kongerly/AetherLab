# AetherLab

AetherLab 是一个模块化 AI 工程平台，计划围绕大语言模型推理、RAG、Agent、评测和可观测性，
逐步构建可运行、可扩展的实验与应用工作流。

> **当前状态：** Pre-Alpha / Phase 0。项目已提供 FastAPI 后端基础，包括健康检查、配置校验、
> JSON 请求日志、带请求 ID 的统一错误响应及 CI 工作流。Phase 0 实现与本地验证已完成，
> 远端 CI 验收尚待确认。AI 平台能力仍处于规划阶段。

## 已实现能力

- 使用 `uv` 管理的 Python 3.13 后端
- FastAPI 应用与 OpenAPI 接口文档
- `GET /health` 健康检查
- Ruff 静态检查与格式化配置
- 健康检查、配置、错误契约和请求上下文测试
- 环境配置校验与后端 dotenv 模板
- JSON 应用日志与服务端生成的 `X-Request-ID` 响应头
- 统一的 HTTP、参数校验、业务异常及未处理异常响应
- 在相关推送和拉取请求中执行后端检查的 GitHub Actions 工作流
- 共享的 VS Code 工作区配置
- 项目设计、路线图、后端设计与工程规范文档

## 后续方向

项目按小而完整的纵向功能逐步推进：

1. 兼容 OpenAI 的 LLM Provider、聊天 API、SSE 流式响应、最小 Web 界面及调用追踪
2. 使用 PostgreSQL 持久化会话
3. 支持可追溯引用与评测的基础 RAG
4. 工具调用与有明确执行边界的 Agent 循环
5. 更完整的评测、可观测性和工作流能力

## 项目文档

- [项目设计](docs/design.md)：稳定的产品方向、设计原则、架构与技术选型
- [开发路线图](docs/roadmap.md)：当前状态、开发阶段与完成条件
- [后端设计](docs/backend.md)：分层、Provider、聊天、SSE、错误、日志与追踪
- [工程规范](docs/engineering.md)：开发流程、代码质量、测试、CI、安全与公开仓库策略

## 环境要求

- Python 3.13
- [uv](https://docs.astral.sh/uv/)

Docker Compose、前端和外部模型服务尚未配置。

## 快速启动

安装锁文件指定的后端依赖：

```bash
cd backend
uv sync --frozen
```

默认配置无需 dotenv 文件即可运行。如需覆盖配置，将 `backend/.env.example` 复制为
`backend/.env`，并设置以下变量：

| 变量 | 默认值 | 可选值 |
| --- | --- | --- |
| `APP_ENV` | `development` | `development`、`test`、`production` |
| `LOG_LEVEL` | `INFO` | `DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL` |

环境变量优先于 dotenv 文件；无效值会导致启动失败。命令从 `backend/` 目录执行，
根目录的 `.env.example` 仅用于指向后端配置模板。

启动开发服务器：

```bash
uv run uvicorn app.main:app --reload --no-access-log
```

服务地址：

- API：<http://127.0.0.1:8000>
- 交互式接口文档：<http://127.0.0.1:8000/docs>
- 健康检查：<http://127.0.0.1:8000/health>

验证健康检查接口：

```bash
curl http://127.0.0.1:8000/health
```

预期响应：

```json
{
  "status": "ok",
  "service": "aetherlab"
}
```

每个 HTTP 响应都包含服务端新生成的 `X-Request-ID`，不会复用传入的请求 ID。
应用以 JSON 格式记录相同的请求 ID、路由模板、状态码、耗时（毫秒）及错误码。
未匹配路由记录为 `<unmatched>`；日志不包含原始路径、查询参数、请求体或异常文本。
保留 `--no-access-log`，避免 Uvicorn 独立的访问日志记录原始 URL。
Uvicorn 生命周期日志沿用其标准格式。`LOG_LEVEL` 控制应用日志，级别高于 `INFO` 时，
不会输出普通请求完成日志。

错误统一使用 `{ "code": "...", "message": "...", "request_id": "..." }` 结构，
覆盖 404、405、参数校验失败，以及响应头发送前发生的未处理异常。
错误消息使用固定文本，不暴露输入值或异常详情。流式响应生命周期处理和分布式追踪属于 Phase 1。

## 开发检查

在 `backend/` 目录执行：

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

测试覆盖健康检查响应、配置校验、错误契约、请求 ID 关联、并发上下文隔离及 JSON 日志脱敏，
无需模型服务或 API 密钥。CI 先执行 `uv sync --frozen` 同步依赖，再运行相同的静态检查、
格式检查和测试。

## 仓库结构

```text
AetherLab/
|-- backend/             FastAPI 后端与 Python 项目配置
|-- frontend/            预留的 React 与 TypeScript 前端目录
|-- docs/                项目文档
|   |-- design.md        稳定的产品与架构方向
|   |-- roadmap.md       当前状态与开发阶段
|   |-- backend.md       后端架构与接口契约
|   `-- engineering.md   仓库工作流与质量标准
|-- scripts/             项目自动化脚本
|-- data/                被 Git 忽略的本地运行数据
|-- .github/             仓库自动化与后端 CI
|-- AGENTS.md            公开的 AI 辅助开发规范
|-- .env.example         后端配置模板的入口说明
|-- docker-compose.yml   预留文件；Phase 0 暂无服务需求
`-- README.md
```

## AI 辅助开发

仓库中的 [AGENTS.md](AGENTS.md) 定义适用于整个项目的 AI 编程协作规范，
其中不包含凭据、私有端点、个人路径或机器专用配置。

如需仅适用于本地检出的私有 Codex 指令：

1. 将 `AGENTS.md` 复制为 `AGENTS.override.md`。
2. 在副本中加入本地指令。
3. 密钥存放在 `.env` 或密钥管理器中，不写入任何 Agent 指令文件。

`AGENTS.override.md` 已被 Git 忽略。Codex 优先使用同目录的此文件，它会替换 `AGENTS.md`，
而不是与之合并。需要跨仓库复用的个人默认指令也可以放在 `~/.codex/AGENTS.md` 中。

查找顺序、作用范围和覆盖行为见 [Codex 官方 AGENTS.md 文档](https://learn.chatgpt.com/docs/agent-configuration/agents-md)。

## 开发原则

- 以小而完整的纵向功能推进开发。
- 避免推测性的抽象和空模块骨架。
- 新增行为时同步添加测试。
- 从首次实现起，让 LLM 操作具备可观测性和可评测性。
- 保持关键 Provider 与基础设施组件可替换。
- 代码标识符、文件名、API 消息、日志和错误使用英文；注释、Docstring 说明和文档优先中文。
- 提交信息可用中文或英文，清楚说明变更目的。
- 不提交密钥、本地数据、模型文件或已填入配置的 `.env` 文件。

## 参与开发

项目仍处于早期阶段。修改前请阅读 [AGENTS.md](AGENTS.md) 和 [`docs/`](docs/) 下的相关文档。
保持文档与实际实现一致，并在发起拉取请求前运行相关检查。

## 许可证

本项目采用 [MIT 许可证](LICENSE)。
