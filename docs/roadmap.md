# AetherLab 开发路线图

本文档记录当前状态、阶段计划和每个阶段的完成条件。它会随实现进度持续更新。

稳定的项目定位与总体架构见 [`design.md`](design.md)，后端设计见
[`backend.md`](backend.md)，工程规范见 [`engineering.md`](engineering.md)。

## 1. 当前状态

```text
Pre-Alpha / Phase 0
```

Phase 0 后端实现与本地验证已完成，远端 CI 验收待确认；Phase 1 尚未开始。

### 1.1 已完成

- Git / GitHub 仓库初始化、基础目录、分职责文档与公开 `AGENTS.md`
- VS Code 项目级配置、uv 锁文件、Python 3.13、Ruff 与 pytest
- FastAPI 应用、`GET /health` 与 OpenAPI
- `backend/.env.example` 与环境变量配置校验
- JSON 应用日志、请求完成日志、耗时与服务端生成的 Request ID
- HTTP、参数校验、自定义资源缺失及未处理异常的统一错误响应
- Health API、配置、错误契约、日志脱敏与并发上下文隔离测试
- Minimal GitHub Actions CI：锁定依赖同步、Lint、Format Check、Test

### 1.2 Phase 0 验收状态

- `uv sync --frozen`、本地 Ruff、Format Check 和 13 项测试通过。
- 真实 Uvicorn 启动、`/health`、OpenAPI 和响应／日志 Request ID 关联验证通过。
- 远端 GitHub Actions 结果尚未核验，不能宣称完整 CI 验收通过。
- Docker Compose 当前无服务需求，保留空文件；按本阶段“实际需要时填写”的原则，
  不将容器化作为本轮完成条件。后续引入模型运行时或数据库时再评估。
- 当前只提供 HTTP 请求关联；Trace ID、LLM Usage 和流式生命周期处理留到 Phase 1。

### 1.3 尚未进入实现

- LLM Provider
- Chat API 与 SSE Streaming
- Frontend
- PostgreSQL 与 Conversation Persistence
- RAG
- Agent
- Evaluation
- Trace / Observability 平台

## 2. 阶段推进原则

- 每个阶段必须形成可以运行和验证的纵向闭环。
- 不为未来阶段预建空模块或空文档。
- 下一阶段只在当前阶段的完成条件满足后启动。
- Observability、Testing 与 Evaluation 随功能一起增长。
- 路线图可以根据验证结果调整，但调整原因应记录在相关文档或提交中。

## 3. Phase 0 — Bootstrap

目标：建立可靠的最小开发基础。

状态：实现及本地检查已完成，待远端 CI 通过后关闭阶段验收。

### 工作内容

- 完成环境变量模板和基础配置模块
- 为 `GET /health` 添加 API 测试
- 建立最小 CI：依赖同步、Lint、Format Check、Test
- 建立结构化日志与统一错误响应的最小实现
- 提供可复现的本地启动方式
- 只在实际需要时填写 Docker Compose 服务

### 完成条件

```text
clone repo
↓
uv sync
↓
tests pass
↓
CI pass
↓
backend starts
↓
/health works
```

## 4. Phase 1 — First Vertical Chat Slice

目标：完成第一条真实的 AI 功能链路。

```text
OpenAI-compatible Provider
↓
Chat API
↓
SSE Streaming
↓
Minimal React Chat UI
↓
Request Trace
↓
Latency / Token / Error Metrics
↓
Tests
```

### 第一阶段范围

- 只实现一个 OpenAI-compatible Provider
- 支持普通 Chat 与 SSE Streaming
- 前端只提供输入、流式输出、基本状态和错误展示
- llama.cpp 作为首个本地模型运行时
- 从第一版调用开始记录 Request ID、Trace ID、耗时、状态、错误和可用的 Token Usage

### 暂不包含

- 多 Provider 并行实现
- 完整设置中心与复杂前端动画
- Conversation Persistence
- LangGraph
- 高级缓存与任务队列

### 完成条件

用户可以通过 Web UI 发送消息并收到模型的流式回答；后端能够记录请求状态、耗时、错误和
基础 Usage，关键路径具备自动化测试。

## 5. Phase 2 — Conversation Persistence

目标：让对话在服务和页面重启后仍然可恢复。

### 工作内容

- PostgreSQL
- SQLAlchemy
- Alembic
- Conversation 与 Message 模型
- Repository 层
- 对话创建、读取和消息持久化

建议的初始实体字段：

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

### 完成条件

刷新页面或重启服务后，用户仍能读取已有对话和消息历史。

## 6. Phase 3 — Basic RAG

目标：完成单知识库、可追溯引用的基础 RAG 闭环。

```text
Document
↓
Parser
↓
Cleaner
↓
Chunker
↓
Embedding
↓
Vector Store

Query
↓
Retriever
↓
Context Builder
↓
LLM
↓
Answer + Citation
```

### 第一阶段范围

- Single Knowledge Base
- Simple Chunking
- Single Embedding Model
- pgvector Vector Search
- Top-K Retrieval
- 可追溯到 Document 与 Chunk 的 Citation
- 基础检索与回答评测

文档摄取应逐步支持 status、checksum、idempotency、retry 与 failure reason，避免重复摄取。

### 暂不包含

- BM25
- Hybrid Search
- Query Rewrite
- Multi-Query
- Complex Reranking

### 完成条件

用户可以上传文档并基于文档提问；回答中的引用能够追溯到具体文档、Chunk、来源元数据和
检索分数。

当本阶段真正开始实现时，再创建 `docs/rag.md` 记录详细设计。

## 7. Phase 4 — Advanced RAG

目标：在基础 RAG 有可重复的评测基线后提升检索质量。

- BM25
- Hybrid Search
- Fusion
- Reranker
- Query Rewrite
- Semantic Chunking
- RAG Evaluation

是否引入每一项能力由评测结果决定，而不是由功能列表决定。

## 8. Phase 5 — Agent

目标：实现可控制、可追踪的基础 Agent Loop。

```text
User
↓
LLM
├── Final Answer
└── Tool Call
      ↓
     Tool
      ↓
Observation
      ↓
     LLM
```

### 第一阶段范围

- 自行实现基础 Agent Loop
- Tool interface 与 registry
- Calculator、DateTime、RAG 等少量可验证工具
- `max_steps`、`max_tool_calls`、timeout、retry 与 fallback
- Tool Call 与 Agent Step trace
- 任务成功率和工具选择准确率等基础评测

复杂 Workflow 出现后再评估 LangGraph。

### 完成条件

Agent 能够在明确的步数、工具次数和超时限制内完成受测任务，并提供完整执行轨迹。

当本阶段真正开始实现时，再创建 `docs/agent.md`。

## 9. Phase 6 — Agent Workflow

目标：支持比基础循环更复杂、可恢复和可人工介入的工作流。

- LangGraph 或经验证的等价方案
- Workflow 与 Planning
- Memory
- Checkpoint
- Human-in-the-loop

### 完成条件

复杂工作流可以暂停、恢复、追踪和人工介入，且失败路径具备清晰状态。

## 10. Phase 7 — Evaluation Platform

目标：把随功能增长的评测能力整合成统一平台。

- Eval Dataset 与版本管理
- Eval Runner
- Model Comparison
- RAG Evaluation
- Agent Evaluation
- Regression Evaluation
- Dashboard

核心指标按能力选择：

- Chat / Model：TTFT、总延迟、Tokens/s、Token Usage、Error Rate
- RAG：Hit Rate、Recall、MRR、Context Precision、Faithfulness、Answer Correctness
- Agent：Task Success、Tool Selection Accuracy、Tool Call Count、Step Count、Failure Rate

当统一评测平台进入实现时，再创建 `docs/evaluation.md`。

## 11. Phase 8 — Scaling & Engineering Expansion

目标：只针对已经观察到的容量、性能或运维问题扩展基础设施。

候选能力包括：

- Redis
- Qdrant
- vLLM
- Advanced Cache
- Background Task Queue
- Go Gateway
- Distributed Service
- Deployment Optimization

这些项目不是默认必做项。引入前应有基准数据、故障模式或业务需求作为依据。

当 Observability 成为独立产品能力时，再创建 `docs/observability.md`。

## 12. 文档维护规则

- 完成或新增里程碑时更新“当前状态”和对应 Phase。
- 阶段范围发生变化时说明原因，并同步相关专项文档。
- `design.md` 不记录每周进度或临时任务。
- `backend.md` 和 `engineering.md` 记录当前有效的约束，不复制本路线图中的状态清单。
