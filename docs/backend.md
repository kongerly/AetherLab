# AetherLab Backend 设计

本文档记录后端分层、核心接口、Chat 与 Streaming、配置、错误和可观测性约束。

当前进度与阶段边界见 [`roadmap.md`](roadmap.md)，代码质量、测试和 CI 规范见
[`engineering.md`](engineering.md)。

## 1. 当前实现

后端当前是 Python 3.13 + FastAPI 的最小应用，入口为 `backend/app/main.py`，已实现：

```http
GET /health
```

当前还没有配置模块、数据库、LLM Provider、Chat API、SSE、统一错误模型或结构化日志。
本文件后续章节描述的是逐步实现时应遵守的设计边界，不代表对应能力已经存在。

## 2. 目录演化

当前目录保持最小：

```text
backend/
├── app/
│   └── main.py
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

配置应集中在 `app/core/config.py`，从环境变量读取，并满足：

- `.env.example` 只包含安全的变量名、说明和非敏感默认值。
- `.env` 不提交 Git。
- 配置在应用启动时完成校验，缺少必需项时给出明确错误。
- API Key 不返回前端、不进入日志、不作为普通配置对象序列化。
- 测试可以显式覆盖配置，不依赖开发者机器环境。

## 5. Logging 与 Request Context

从第一条真实 Chat 链路开始使用结构化日志。HTTP 请求的最小字段为：

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

外部 API 使用统一、稳定的错误结构，例如：

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

```python
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

Retrieval Span 记录 query、top_k、document_id、chunk_id 与 score；Tool Span 记录 tool_name、
status 和 latency。Tool arguments 只有在完成敏感信息处理后才可记录。

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
