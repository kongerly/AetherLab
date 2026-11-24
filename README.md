# AetherLab

AetherLab 是一个面向 AI Engineering 的模块化实验与应用平台，计划围绕大语言模型推理、RAG、Agent、评测与可观测性，按小而完整的纵向闭环逐步构建可运行、可扩展的工程工作流。

> **当前状态：** Pre-Alpha（Phase 0 已完成并通过本地与远端 CI 验收）。当前已提供 FastAPI 后端工程基础；Phase 1 尚未开始，AI 平台核心能力仍处于规划阶段。

## 当前能力

- **后端服务基础**
  - 基于 `uv` 管理的 Python 3.13 FastAPI 应用，提供 `GET /health` 健康检查与 OpenAPI 交互式文档
  - 基于 `pydantic-settings` 的启动期环境变量校验与 `backend/.env.example` 配置模板
  - 服务端生成的 `X-Request-ID`、脱敏 JSON 应用日志，以及覆盖 HTTP、参数校验、业务异常与未处理异常的统一错误响应
- **工程与质量保障**
  - 覆盖健康检查、配置校验、错误契约、请求 ID 关联、并发上下文隔离与日志脱敏的 `pytest` 测试套件
  - 统一的 Ruff 静态检查与格式化配置
  - 在相关推送与 Pull Request 中自动运行后端检查的 GitHub Actions CI 工作流
  - 共享的 VS Code 工作区配置，以及分职责的项目设计、路线图、后端设计与工程规范文档

## 演进路线

以下能力均处于**规划阶段**（尚未进入实现），将按小而完整的纵向闭环逐步推进：

1. **Phase 1 — 首个聊天纵向闭环**：OpenAI-compatible LLM Provider、Chat API、SSE 流式响应、最小 Web 界面，以及请求级 Trace 与 Token Usage 记录
2. **Phase 2 — 会话持久化**：基于 PostgreSQL、SQLAlchemy 与 Alembic 持久化对话和消息历史
3. **Phase 3–4 — RAG 能力**：先完成可追溯引用与基础评测的单知识库 RAG，再依据评测结果引入检索增强
4. **Phase 5–6 — Agent 与工作流**：具备明确执行边界的工具调用、基础 Agent 循环与可恢复工作流
5. **Phase 7–8 — 评测平台与按需扩展**：统一评测平台、可观测性深化，以及仅在真实瓶颈出现后引入的基础设施扩展

各阶段详细范围与完成条件见 [开发路线图](docs/roadmap.md)。

## 项目文档

| 文档 | 说明 |
| --- | --- |
| [项目设计](docs/design.md) | 稳定的产品定位、核心原则、总体架构与技术方向 |
| [开发路线图](docs/roadmap.md) | 当前实现状态、阶段规划与验收完成条件 |
| [后端设计](docs/backend.md) | 后端分层、Provider、Chat、SSE、错误、日志与追踪约束 |
| [工程规范](docs/engineering.md) | 开发工作流、代码质量、测试、CI、安全与公开仓库策略 |

## 环境要求

- Python `3.13.17`（开发与 CI 精确基线；支持范围为 `>=3.13.17,<3.14`）
- [uv](https://docs.astral.sh/uv/) `0.13.4` 或更新版本

当前尚未配置 Docker Compose、前端及外部模型服务。

## 快速启动

### 1. 安装依赖

先安装 Python `3.13.17`；若 `uv python install 3.13.17` 暂未提供该版本，可直接使用 [Python 3.13.17 官方发行版](https://www.python.org/downloads/release/python-31317/)。随后安装锁文件指定的后端依赖：

```bash
cd backend
uv sync --frozen
```

### 2. 配置环境变量（可选）

使用默认配置无需 `.env` 文件即可启动。如需覆盖，将 `backend/.env.example` 复制为 `backend/.env`：

| 变量 | 默认值 | 可选值 |
| --- | --- | --- |
| `APP_ENV` | `development` | `development`、`test`、`production` |
| `LOG_LEVEL` | `INFO` | `DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL` |

配置优先级为 **环境变量 > `backend/.env` > 默认值**，无效值会导致启动失败。所有后端命令均在 `backend/` 目录执行；根目录的 `.env.example` 仅作入口说明，不会被后端加载。

### 3. 启动开发服务器

```bash
uv run uvicorn app.main:app --reload --no-access-log
```

> 保留 `--no-access-log`，避免 Uvicorn 默认访问日志输出原始 URL。

启动后的本地访问地址：

- API：<http://127.0.0.1:8000>
- 交互式接口文档：<http://127.0.0.1:8000/docs>
- 健康检查：<http://127.0.0.1:8000/health>

### 4. 验证健康检查

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

### 升级已有虚拟环境

仅修改版本文件不会自动升级已有 `.venv`。进行 Python 安全补丁或版本升级时，请先备份旧环境，在 `backend/` 目录下重建 `.venv`、同步依赖并核对实际版本（若解释器未被自动发现，可将 `--python` 参数替换为新解释器的完整路径）：

```bash
uv venv --python 3.13.17
uv sync --frozen
uv run --frozen python -c "import sys; print(sys.executable); print(sys.version)"
```

确认版本号一致并通过下方开发检查后再清理备份。项目本地解释器与临时备份可放在已被 Git 忽略的 `.python-runtime/` 目录中。

## 运行时约定

- **请求 ID 关联**：每个 HTTP 响应均附带服务端新生成的 `X-Request-ID`，不会复用客户端传入值，并在错误响应与应用日志中使用同一个 ID。
- **结构化脱敏日志**：应用以 JSON 格式记录请求 ID、方法、路由模板、状态码、耗时（毫秒）及错误码；未匹配路由记为 `<unmatched>`，不记录原始路径、查询参数、请求头、请求体或异常文本。Uvicorn 生命周期日志沿用标准格式；`LOG_LEVEL` 高于 `INFO` 时不会输出普通请求完成日志。
- **统一错误契约**：统一覆盖 404、405、参数校验失败（422）、业务资源缺失，以及响应头发送前发生的未处理异常（500）。错误消息为固定英文文本，不暴露用户输入、异常详情或堆栈：

```json
{
  "code": "...",
  "message": "...",
  "request_id": "..."
}
```

> 流式响应生命周期处理与分布式追踪（Trace ID）属于 Phase 1 范围，当前版本仅提供 HTTP 请求级关联。

## 开发检查

在 `backend/` 目录下运行静态检查、格式检查与测试：

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

测试覆盖健康检查响应、配置校验、错误契约、请求 ID 关联、并发上下文隔离及 JSON 日志脱敏，无需外部模型服务或 API Key。GitHub Actions CI 会先执行 `uv sync --frozen` 同步依赖并断言 Python 版本，再使用 `uv run --frozen` 运行相同的三项检查。

## 仓库结构

```text
AetherLab/
├── backend/             # FastAPI 后端与 Python 项目配置
├── frontend/            # 预留的 React 与 TypeScript 前端目录
├── docs/                # 项目文档
│   ├── design.md        # 稳定的产品定位与总体架构
│   ├── roadmap.md       # 当前状态与开发阶段
│   ├── backend.md       # 后端架构与接口契约
│   └── engineering.md   # 仓库工作流与质量标准
├── scripts/             # 项目自动化脚本（按需添加）
├── data/                # 被 Git 忽略的本地运行数据
├── .github/             # 仓库自动化与后端 CI 工作流
├── .vscode/             # 共享的 VS Code 工作区配置
├── AGENTS.md            # 公开的项目级 AI 辅助开发规范
├── .env.example         # 指向后端配置模板的入口说明
├── docker-compose.yml   # 预留文件（Phase 0 暂无服务需求）
├── LICENSE              # MIT 许可证
└── README.md
```

## 开发原则

- **纵向闭环优先**：以小而完整的纵向功能推进开发，避免推测性抽象与空模块骨架。
- **测试同步演进**：新增行为时同步补充能验证外部表现的自动化测试。
- **可观测与可评测**：从首条 LLM 链路起内建可观测性与可评测性。
- **核心组件可替换**：保持关键 Provider 与基础设施组件通过清晰接口解耦。
- **明确的语言规范**：代码标识符、文件名、API 消息、日志与错误使用英文；注释、Docstring 说明与项目文档优先中文；提交信息中英文均可，需清晰说明变更目的。
- **严格的安全边界**：不提交密钥、本地数据、模型文件或已填入配置的 `.env` 文件。

## 参与开发

项目仍处于早期阶段。提交变更前，请先阅读 [AGENTS.md](AGENTS.md) 与 [`docs/`](docs/) 下的相关文档，保持文档与实际实现一致，并在发起 Pull Request 前运行相关开发检查。

## 许可证

本项目采用 [MIT 许可证](LICENSE)。
