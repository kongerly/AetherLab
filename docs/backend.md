# AetherLab Backend 设计

本文档记录后端分层、核心接口、Chat 与 Streaming、配置、错误和可观测性约束。

当前进度与阶段边界见 [`roadmap.md`](roadmap.md)，代码质量、测试和 CI 规范见
[`engineering.md`](engineering.md)。

## 1. 当前实现

后端当前是 Python 3.13 + FastAPI 的最小应用，入口为 `backend/app/main.py`，已实现：

```http
GET /health
```

已实现环境配置、JSON 应用日志、HTTP 请求关联、统一错误响应及自动化测试。
尚未实现数据库、LLM Provider、Chat API、SSE、Trace ID 或 Token Usage。
后续章节中关于这些能力的内容仍是设计约束。

## 2. 目录演化

当前目录保持最小：

```text
backend/
├── app/
│   ├── main.py
│   ├── api/routes/health.py
│   └── core/
│       ├── config.py
│       ├── exceptions.py
│       ├── logging.py
│       └── middleware.py
├── tests/
│   ├── test_health.py
│   ├── test_config.py
│   └── test_http_foundation.py
├── .env.example
├── .python-version
├── pyproject.toml
└── uv.lock
```

随着实际功能增长，可以逐步演化为：

```text
app/
├── api/
├── core/
├── db/
├── models/
├── schemas/
├── repositories/
├── services/
├── llm/
├── rag/
├── agent/
├── eval/
├── observability/
└── main.py
```

只有在对应纵向功能进入实现时才创建目录，禁止为未来功能预建空包。

## 3. 分层设计

### 3.1 API Layer

负责：

- 路由与协议处理
- 请求参数解析和校验
- 调用 Service
- 将领域结果转换为 Response

API 层不堆积复杂业务流程，不直接操作数据库或绑定具体模型供应商。

### 3.2 Service Layer

负责业务流程编排，例如：

- `ChatService`
- `ModelService`
- `ConversationService`
- `RAGService`
- `AgentService`
- `EvalService`

Service 面向内部接口工作，不将 HTTP 或具体 SDK 的细节扩散到业务层。

### 3.3 Repository Layer

负责持久化访问和事务边界。业务层不直接依赖 SQLAlchemy Query 或具体数据库结构。

### 3.4 Models 与 Schemas

- Models 表达数据库实体。
- Schemas 表达 API 请求、响应和跨层数据结构。
- 不复用数据库 Model 作为外部 API 契约。

### 3.5 依赖方向

```text
API Route
    │
    ▼
 Service
    │
    ▼
Repository / Provider
    │
    ▼
Database / Model Runtime
```

上层依赖抽象，具体基础设施实现不反向控制业务接口。

## 4. Configuration

配置已集中在 `app/core/config.py`，使用 `pydantic-settings`，启动时校验。
从 `backend/` 启动时读取该目录的 `.env`；环境变量优先于 dotenv，dotenv 优先于默认值。
模板为 `backend/.env.example`；根目录模板仅作指引。

| 配置 | 默认值 | 合法值 |
| --- | --- | --- |
| `APP_ENV` | `development` | `development`、`test`、`production` |
| `LOG_LEVEL` | `INFO` | `DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL` |

`APP_ENV` 当前仅保存环境标记，不启用额外环境专属行为。
后续扩展继续满足：

- `.env.example` 只包含安全的变量名、说明和非敏感默认值。
- `.env` 不提交 Git。
- 配置在应用启动时完成校验，缺少必需项时给出明确错误。
- API Key 不返回前端、不进入日志、不作为普通配置对象序列化。
- 测试可以显式覆盖配置，不依赖开发者机器环境。

## 5. Logging 与 Request Context

当前 `app` logger 输出 JSON。HTTP 中间件为每个请求生成 UUID4，不复用客户端
`X-Request-ID`，并写入响应同名头、`request.state.request_id` 与 ContextVar。
错误响应和请求完成日志使用同一个 ID，请求结束后恢复上下文。

当前请求完成日志包含 `timestamp`、`level`、`logger`、`message`、`request_id`、
`method`、`route`、`status`、`latency_ms`、`error`。`route` 只记录路由模板，
未匹配时为 `<unmatched>`；不记录原始 URL、请求头、正文或异常文本。
普通完成日志为 INFO，5xx 或未处理异常为 ERROR；配置更高日志等级会过滤相应记录。
启动命令使用 `--no-access-log`，避免 Uvicorn 另行输出原始 URL；其生命周期日志保持默认格式。
此策略不自动净化未来业务代码主动写入的日志消息，调用者仍须遵守数据安全约束。

Phase 1 再补充 Trace ID 和 LLM 调用记录，目标 HTTP 字段为：

```text
timestamp
level
request_id
trace_id
route
status
latency
error
```

LLM 调用额外记录：

```text
provider
model
prompt_tokens
completion_tokens
total_tokens
```

约束：

- Request ID 与 Trace ID 应贯穿 API、Service 和 Provider。
- Token Usage 不可用时允许为空，不伪造数值。
- 日志记录错误类别和必要上下文，不记录密钥、授权头或未脱敏的敏感内容。
- 流式请求也必须记录结束、取消、超时和中断状态。

## 6. Error Model

当前外部错误响应统一包含 `code`、`message`、`request_id`：

| 情况 | HTTP 状态 | code |
| --- | --- | --- |
| 路由不存在 | 404 | `NOT_FOUND` |
| 方法不支持 | 405 | `METHOD_NOT_ALLOWED` |
| 请求参数校验失败 | 422 | `VALIDATION_ERROR` |
| `ResourceNotFoundError` | 404 | `RESOURCE_NOT_FOUND` |
| 发送响应头前的未处理异常 | 500 | `INTERNAL_SERVER_ERROR` |

其他 HTTP 异常使用标准 HTTP 状态名称作为 code，非标准状态使用 `HTTP_ERROR`。
响应保留 `Allow`、`WWW-Authenticate` 等协议头。message 使用固定英文文本，
不回显异常正文或校验输入；500 不返回堆栈。响应头发送后的异常不能改写为 JSON，
会记录错误并向服务器传播；SSE 的取消、中断和错误事件契约在 Phase 1 实现。

未来 Provider 错误也遵循这一结构，例如：

```json
{
  "code": "MODEL_UNAVAILABLE",
  "message": "Model service unavailable",
  "request_id": "xxx"
}
```

Provider 层逐步统一以下错误语义：

- Timeout
- Authentication Error
- Rate Limit
- Invalid Request
- Provider Unavailable
- Generation Error
- Streaming Error
- Client Cancellation

内部异常不直接暴露堆栈、凭据、上游响应正文或实现细节。API 状态码、错误代码和重试语义
必须保持一致。

## 7. LLM Provider

### 7.1 目标

业务层不直接依赖 OpenAI、llama.cpp 或其他具体 SDK。统一接口至少覆盖普通生成和流式生成：

以下为接口形状示意，并非可执行 Python 代码：

```text
class LLMProvider:
    async def chat(...):
        ...

    async def stream(...):
        ...
```

实际实现时应使用清晰的类型表达请求、响应、流事件、Usage 和错误，而不是让供应商原始对象
穿透到 Service 或 API 层。

### 7.2 第一阶段范围

只实现一个 `OpenAICompatibleProvider`。它可以连接 llama.cpp 和提供 OpenAI-compatible API
的云服务，用一个实现验证抽象是否合理。

不要为了展示扩展性同时实现多个功能重复的 Provider。

### 7.3 Provider Capability

不同模型能力必须显式描述，不能假设完全一致。后续 Capability 可以包括：

- Streaming
- Tool Calling
- Structured Output
- Vision
- Embeddings
- Usage Statistics
- Reasoning

调用前根据能力校验请求；能力缺失时返回稳定的内部错误。

## 8. Chat API

第一条纵向闭环计划提供：

```text
POST /api/v1/chat
POST /api/v1/chat/stream
```

调用链：

```text
User
↓
Web UI
↓
Chat API
↓
ChatService
↓
LLM Provider
↓
Response / Stream
```

普通与流式端点应尽量共享请求模型、业务校验和 Provider 选择逻辑，避免两套行为逐渐分叉。

## 9. SSE Streaming

第一版 Streaming 使用 Server-Sent Events，不使用 WebSocket。

需要覆盖的生命周期：

- 建立连接
- 内容增量事件
- Usage 或完成元数据
- 正常结束
- Provider 错误
- 超时
- 客户端断开与请求取消
- 流中断后的资源释放

事件类型和载荷应被明确建模并形成稳定契约。后端发现客户端断开后，应尽快取消上游生成，
并记录终止状态。

## 10. Chat Trace

第一版 Chat 至少记录：

```text
request_id
trace_id
provider
model
start_time
end_time
latency
status
error
prompt_tokens
completion_tokens
total_tokens
```

Trace 后续扩展为树状结构：

```text
Trace
├── LLM Call
├── Retrieval
├── Rerank
├── Tool Call
└── Agent Step
```

Retrieval Span 记录 top_k、document_id、chunk_id 与 score；Tool Span 记录 tool_name、
status 和 latency。query 与 Tool arguments 默认不记录，仅在明确脱敏策略并完成敏感信息处理后
才可记录；文档与分块标识也不得直接包含私人路径或用户原文。

## 11. Conversation Persistence

Chat 纵向闭环稳定后引入 PostgreSQL、SQLAlchemy 与 Alembic。初始实体为：

```text
Conversation
├── id
├── title
├── model_id
├── created_at
└── updated_at

Message
├── id
├── conversation_id
├── role
├── content
├── prompt_tokens
├── completion_tokens
├── latency
├── metadata
└── created_at
```

迁移文件必须与 Model 变更一起提交；Schema 演化需要兼顾已有数据，而不是依赖删除数据库
重新开始。

## 12. llama.cpp 集成

推荐将模型运行时与 FastAPI 进程分离：

```text
GGUF
↓
llama-server
↓
OpenAI-compatible API
↓
AetherLab Backend
```

同一个 llama.cpp 服务可以被 AetherLab 与社区 Web UI 分别使用：社区 UI 用于模型、Prompt 和
Sampling 参数调试；AetherLab 负责 Chat、RAG、Agent、Evaluation 与 Trace。

## 13. 后端设计边界

- 不在 API Route 中直接调用模型 SDK 或数据库。
- 不让供应商异常和响应对象穿透内部边界。
- 不在第一阶段引入多个 Provider、LangGraph、Redis、Qdrant 或任务队列。
- 不为未来服务创建空接口和空目录。
- 不记录密钥和未经评估的敏感输入。
- 行为变化应有对应测试，并同步更新本文档或 API 文档。
