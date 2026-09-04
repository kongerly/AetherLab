# AetherLab 项目设计文档

## 1. 项目概述

### 1.1 项目名称

**AetherLab**

项目描述：

> A modular AI Engineering platform for LLM inference, RAG, Agents, evaluation and observability.

### 1.2 当前项目状态

AetherLab 当前处于：

```text
Pre-Alpha / Phase 0
```

当前已经完成：

- Git / GitHub 仓库初始化
- 基础目录结构
- 项目设计文档
- VS Code 项目级配置
- uv Python 环境管理
- Python 3.13
- Ruff 代码规范
- pytest 开发依赖
- FastAPI 基础应用
- `GET /health`
- Swagger / OpenAPI 基础验证

当前尚未完成：

- README 正式内容
- `.env.example` 正式内容
- Docker Compose 服务定义
- 自动化测试
- CI
- 配置管理
- Logging
- 统一错误模型
- LLM Provider
- Chat API
- SSE Streaming
- Frontend
- PostgreSQL
- Conversation Persistence
- RAG
- Agent
- Evaluation
- Trace / Observability

因此当前项目应被视为：

> **方向和架构已经明确，但实际功能仍处于最早期工程脚手架阶段。**

## 2. 项目定位

AetherLab 是一个面向 AI Engineering 的模块化实验与应用平台。

围绕大语言模型构建统一的：

- LLM Provider
- Local / Cloud Inference
- Chat
- RAG
- Agent
- Tool Calling
- Memory
- Evaluation
- Observability
- Persistence
- Web UI

项目不是简单的聊天机器人，也不是单纯封装第三方模型 API。

核心目标是实现一个：

> **可运行、可扩展、可替换、可调试、可观测、可评测的 AI Engineering Platform。**

## 3. 项目原则

### 3.1 AI First

项目核心始终围绕：

```text
LLM
RAG
Agent
Evaluation
Observability
```

前端、数据库、部署等工程能力服务于 AI 系统，而不是让项目演化成普通 CRUD 系统。

### 3.2 Vertical Slice First

开发过程中优先完成：

> **小而完整的纵向闭环**

而不是同时铺开大量模块。

错误方式：

```text
先创建 LLM/
再创建 RAG/
再创建 Agent/
再创建 Eval/
再创建 Trace/
但都没有完整功能
```

推荐方式：

```text
一个 Provider
↓
一个 Chat API
↓
Streaming
↓
Minimal Frontend
↓
Trace
↓
Tests
↓
形成完整可演示闭环
```

### 3.3 Understand Before Framework

核心能力优先理解和实现基础版本。

例如：

```text
Provider abstraction
Retriever
RAG pipeline
Tool calling
Agent loop
```

理解后再引入：

```text
LangGraph
高级 RAG 框架
其他高层抽象
```

### 3.4 Observable From Day One

Observability 不放到项目后期。

从第一条 LLM 调用链开始记录：

```text
Provider
Model
Latency
Status
Error
Prompt Tokens
Completion Tokens
Total Tokens
Request ID
Trace ID
```

后续再扩展到：

```text
Retrieval
Rerank
Tool Call
Agent Step
```

### 3.5 Test Early

测试不是最后补。

每完成一个纵向功能，就增加对应测试。

例如：

```text
Health Endpoint
→ API Test

Provider
→ Provider Unit Test

Chat
→ Chat Integration Test

RAG
→ Retrieval Evaluation
```

### 3.6 Evaluatable

任何重要 AI 模块修改后，都应能够回答：

> 到底变好了还是变差了？

### 3.7 Replaceable

关键组件尽量通过接口解耦：

```text
LLM
Embedding
Retriever
Reranker
Vector Store
Tool
```

### 3.8 Incremental

项目演化顺序：

```text
Simple
↓
Usable
↓
Observable
↓
Evaluatable
↓
Scalable
```

避免过度设计。

## 4. 总体架构愿景

```text
┌──────────────────────────────────────────────┐
│                   Web UI                     │
│                                              │
│ Chat / Knowledge / Agent / Eval / Dashboard │
└──────────────────────┬───────────────────────┘
                       │
                 HTTP / SSE
                       │
┌──────────────────────▼───────────────────────┐
│                 FastAPI Backend              │
│                                              │
│        API / Service / Business Logic        │
└───────┬──────────┬──────────┬─────────┬──────┘
        │          │          │         │
        ▼          ▼          ▼         ▼
      LLM        RAG        Agent     Eval
     Layer      Engine      Engine    Engine
        │          │          │
        │          │          ├──────── Tool System
        │          │          │
        │          └──────── Retriever / Reranker
        │
        ▼
┌──────────────────────────────────────────────┐
│                 Model Runtime                │
│                                              │
│ llama.cpp / Cloud API / Ollama / vLLM       │
└──────────────────────────────────────────────┘

               Data Infrastructure

┌──────────────┐ ┌──────────────┐ ┌─────────────┐
│ PostgreSQL   │ │   pgvector   │ │    Redis    │
│              │ │              │ │  Optional   │
│ metadata     │ │ embedding    │ │ cache/task  │
└──────────────┘ └──────────────┘ └─────────────┘
```

这张图描述的是最终架构愿景，不代表当前全部已经实现。

## 5. 技术栈

### 5.1 核心语言

```text
Python
TypeScript
SQL
```

### 5.2 Backend

```text
Python 3.13
FastAPI
Pydantic
SQLAlchemy
Alembic
asyncio
pytest
Ruff
uv
```

### 5.3 AI / ML

```text
PyTorch
Transformers
Hugging Face
Sentence Transformers
PEFT
```

### 5.4 LLM Runtime

初期：

```text
OpenAI-compatible API
llama.cpp
```

可选：

```text
Ollama
```

后期：

```text
vLLM
```

### 5.5 Database

初期：

```text
PostgreSQL
pgvector
```

按需求后续增加：

```text
Redis
Qdrant
```

### 5.6 Frontend

```text
React
TypeScript
Vite
```

必要时：

```text
React Router
TanStack Query
Zustand
ECharts
```

### 5.7 Engineering

```text
Git
GitHub
Docker
Docker Compose
GitHub Actions
VS Code
```

## 6. 当前推荐项目结构

```text
AetherLab/
│
├── backend/
│   ├── app/
│   │   └── main.py
│   │
│   ├── tests/
│   ├── .python-version
│   ├── pyproject.toml
│   └── uv.lock
│
├── frontend/
│
├── docs/
│   └── design.md
│
├── scripts/
│
├── data/
│   └── .gitkeep
│
├── .github/
│   └── workflows/
│
├── .vscode/
│   ├── extensions.json
│   ├── launch.json
│   └── settings.json
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
└── LICENSE
```

原则：

> 不提前创建大量空模块。

只有在真正开始对应功能时，才增加：

```text
app/core/
app/api/
app/services/
app/repositories/
app/llm/
app/rag/
app/agent/
app/eval/
app/observability/
```

## 7. Backend 分层设计

随着项目增长，Backend 逐步演化为：

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

### 7.1 API Layer

负责：

```text
参数解析
参数校验
调用 Service
返回 Response
```

不堆积复杂业务逻辑。

### 7.2 Service Layer

负责业务流程。

例如：

```text
ChatService
ModelService
ConversationService
RAGService
AgentService
EvalService
```

### 7.3 Repository Layer

负责数据库访问。

### 7.4 Models

SQLAlchemy ORM Model。

### 7.5 Schemas

Pydantic Request / Response Model。

### 7.6 分层关系

```text
API Route
    │
    ▼
 Service
    │
    ▼
Repository
    │
    ▼
 Database
```

## 8. 基础工程能力

这些能力必须前移，而不是留到项目最后。

### 8.1 Configuration

建立统一：

```text
app/core/config.py
```

环境变量从：

```text
.env
```

读取。

公开仓库只提交：

```text
.env.example
```

### 8.2 Logging

从 Chat 第一版开始建立结构化日志。

最少记录：

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

### 8.3 Error Model

统一 API Error 结构：

```json
{
  "code": "MODEL_UNAVAILABLE",
  "message": "Model service unavailable",
  "request_id": "xxx"
}
```

Provider 层还需要逐步统一：

```text
Timeout
Authentication Error
Rate Limit
Invalid Request
Provider Unavailable
Generation Error
Streaming Error
```

### 8.4 Testing

从 Phase 0 开始。

包含：

```text
Unit Test
API Test
Integration Test
Evaluation Test
```

当前首先补：

```text
GET /health
```

测试。

### 8.5 CI

最小 GitHub Actions：

```text
uv sync
ruff check
ruff format --check
pytest
```

每次 push / pull request 自动执行。

## 9. LLM Provider 设计

### 9.1 目标

业务层不直接依赖 OpenAI、llama.cpp 或其他具体接口。

统一抽象：

```python
class LLMProvider:
    async def chat(...):
        ...

    async def stream(...):
        ...
```

### 9.2 第一阶段范围

**只实现一个 OpenAI-compatible Provider。**

原因：

- llama.cpp 本身兼容 OpenAI API
- 很多云服务也提供 OpenAI-compatible endpoint
- 可以先验证 Provider abstraction
- 避免过早实现多个重复 Provider

第一阶段：

```text
OpenAICompatibleProvider
```

即可支持：

```text
llama.cpp
部分 Cloud API
未来其他兼容服务
```

### 9.3 Provider 能力

后续需要显式描述 Provider Capability：

```text
Streaming
Tool Calling
Structured Output
Vision
Embeddings
Usage Statistics
Reasoning
```

不同模型不应假设具备完全相同能力。

### 9.4 Provider 错误语义

不同上游错误需要转换成 AetherLab 内部统一错误。

## 10. Chat 系统设计

第一条真正的纵向闭环：

```text
User
↓
Web UI
↓
POST /chat
↓
ChatService
↓
LLM Provider
↓
Streaming
↓
Frontend
```

### 10.1 Chat API

第一阶段设计：

```text
POST /api/v1/chat
POST /api/v1/chat/stream
```

其中：

```text
/chat/stream
```

使用 SSE。

### 10.2 SSE

第一阶段使用 SSE 而不是 WebSocket。

需要逐步处理：

```text
client disconnect
request cancellation
timeout
provider error
stream interruption
```

### 10.3 Chat Trace

从第一版 Chat 就记录：

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
```

如果上游暂时不返回 Token Usage，则允许字段为空。

## 11. Minimal Frontend

第一阶段前端只做最小闭环。

目标：

```text
输入消息
↓
发送 Chat Request
↓
显示 Streaming Response
↓
显示基本状态
```

不优先实现：

```text
复杂样式
动画
完整设置中心
多页面 Dashboard
```

第一版 Chat UI 足够验证：

```text
API
Streaming
Error
Provider
Latency
```

## 12. Conversation Persistence

在 Chat 纵向闭环稳定后加入 PostgreSQL。

主要实体：

```text
Conversation
Message
```

### 12.1 Conversation

```text
id
title
model_id
created_at
updated_at
```

### 12.2 Message

```text
id
conversation_id
role
content
prompt_tokens
completion_tokens
latency
metadata
created_at
```

## 13. RAG 系统

RAG 在 Chat + Persistence 闭环之后进入。

### 13.1 Document Ingestion

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
```

### 13.2 Query

```text
Query
↓
Embedding
↓
Retriever
↓
Candidate Chunks
↓
Reranker
↓
Context Builder
↓
LLM
↓
Answer + Citation
```

### 13.3 第一阶段范围

只实现：

```text
Single Knowledge Base
Simple Chunking
Single Embedding Model
Vector Search
Top-K Retrieval
Citation
```

不要第一版就加入：

```text
BM25
Hybrid Search
Query Rewrite
Multi-Query
Complex Reranking
```

### 13.4 文档摄取

需要逐步加入：

```text
status
checksum
idempotency
retry
failure reason
```

避免相同文档重复摄取。

### 13.5 Citation Traceability

回答中的 Citation 必须能够追溯到：

```text
knowledge_base
document
chunk
source metadata
retrieval score
```

## 14. Advanced RAG

基础 RAG 稳定后再加入：

```text
BM25
Hybrid Search
Fusion
Reranker
Query Rewrite
Semantic Chunking
RAG Evaluation
```

## 15. Agent 系统

Agent 必须在 Chat 和 RAG 基础能力稳定后进入。

### 15.1 Basic Agent Loop

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

### 15.2 Tool System

统一：

```python
class Tool:
    name: str
    description: str
    input_schema: dict

    async def execute(self, arguments):
        ...
```

第一批 Tool：

```text
CalculatorTool
DateTimeTool
RAGTool
```

### 15.3 Agent Execution Limits

必须支持：

```text
max_steps
max_tool_calls
timeout
retry
fallback
```

### 15.4 LangGraph

第一阶段 Agent Loop 自己实现。

复杂 Workflow 再引入：

```text
LangGraph
```

## 16. Evaluation

Evaluation 不再被视为最后独立追加的模块。

它分阶段伴随各功能增长。

### 16.1 Chat / Model

记录：

```text
TTFT
Total Latency
Tokens / Second
Prompt Tokens
Completion Tokens
Total Tokens
Error Rate
```

### 16.2 RAG

记录：

```text
Hit Rate
Recall
MRR
Context Precision
Context Recall
Faithfulness
Answer Correctness
```

### 16.3 Agent

记录：

```text
Task Success
Tool Selection Accuracy
Tool Call Count
Step Count
Failure Rate
Latency
Token Usage
```

### 16.4 Versioning

后续应给以下对象增加版本概念：

```text
Prompt
Model Config
Retriever Config
Reranker Config
Eval Dataset
Agent Config
```

否则不同评测结果不可复现。

## 17. Observability

Observability 是横跨整个项目的能力。

### 17.1 Trace

```text
Trace
├── LLM Call
├── Retrieval
├── Rerank
├── Tool Call
└── Agent Step
```

### 17.2 Trace 最小字段

```text
trace_id
request_id
status
start_time
end_time
latency
error
```

LLM：

```text
provider
model
prompt_tokens
completion_tokens
```

Retrieval：

```text
query
top_k
document_id
chunk_id
score
```

Tool：

```text
tool_name
arguments
status
latency
```

## 18. Security

第一阶段不做复杂多租户系统，但设计时必须避免未来无法扩展。

需要逐步考虑：

```text
API Key storage
Authentication
Authorization
Sensitive log filtering
Data isolation
Upload validation
Prompt injection
Tool permission boundaries
```

API Key 不得：

```text
明文返回给前端
写入日志
提交 Git
```

## 19. llama.cpp 集成

推荐：

```text
GGUF
↓
llama-server
↓
OpenAI-compatible API
↓
AetherLab Backend
```

llama.cpp 独立于 FastAPI 进程。

### 19.1 社区 Web UI

可以同时使用：

```text
                 llama.cpp
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
AetherLab Backend          Community Web UI
```

Community Web UI：

```text
模型测试
Prompt 测试
Sampling 参数调试
```

AetherLab：

```text
Chat
RAG
Agent
Eval
Trace
Knowledge
```

## 20. GitHub 与公开策略

AetherLab 使用公开仓库。

公开：

```text
README.md
LICENSE
.env.example
.gitignore
.gitattributes
.editorconfig
docker-compose.yml
.vscode 项目级共享配置
backend/
frontend/
docs/
tests/
GitHub Actions
公开示例数据
```

不公开：

```text
.env
API Key
Password
Token
Cookie
真实用户数据
本地模型文件
日志
缓存
.venv
node_modules
大量本地数据
```

## 21. 代码与文档语言规范

```text
代码                         英文
变量 / 函数 / 类名            英文
文件名                       英文
正式代码注释                  英文
Docstring                    英文
Commit Message              英文
API / Log / Error Message   英文
README.md                   英文为主
docs/design.md              中文
开发临时注释                  可中文
```

开发过程中允许临时中文注释。

提交前将需要长期保留的注释整理成简洁英文。

## 22. Python 代码规范

命名：

```text
文件名          snake_case.py
变量            snake_case
函数            snake_case
类              PascalCase
常量            UPPER_SNAKE_CASE
私有成员        _leading_underscore
```

要求：

- 尽量使用类型注解
- 公共函数和类使用 Docstring
- 普通注释解释 Why，而不是重复 What
- Ruff 负责格式化和 Lint
- pytest 负责测试

## 23. 执行路线图

### Phase 0 — Bootstrap

目标：

> 建立可靠的最小开发基础。

#### 已完成

- Git Repository
- GitHub Repository
- Basic Directory Structure
- Design Document
- VS Code Workspace Config
- uv
- Python 3.13
- Ruff
- pytest dependency
- FastAPI
- `GET /health`

#### 接下来补齐

- README
- `.env.example`
- `.gitattributes`
- `.editorconfig`
- Health API Test
- Minimal GitHub Actions CI
- Basic Config
- Basic Logging
- Basic Error Model

完成条件：

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

### Phase 1 — First Vertical Chat Slice

只做一条完整链路。

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

完成条件：

> 用户可以通过 Web UI 发送消息，模型流式返回回答，同时后端能够记录请求状态、耗时和基础 Usage。

### Phase 2 — Conversation Persistence

加入：

```text
PostgreSQL
SQLAlchemy
Alembic
Conversation
Message
```

完成条件：

> 刷新页面后历史对话仍然存在。

### Phase 3 — Basic RAG

加入：

```text
Knowledge Base
Document Upload
Parser
Chunker
Embedding
pgvector
Vector Retrieval
Citation
RAG Test
```

完成条件：

> 用户可以上传文档，并通过 Chat 基于文档回答，同时引用可追溯到具体 Chunk。

### Phase 4 — Advanced RAG

加入：

```text
BM25
Hybrid Search
Fusion
Reranker
Query Rewrite
RAG Evaluation
```

### Phase 5 — Agent

加入：

```text
Tool Calling
Tool Registry
Agent Loop
Agent State
Agent Trace
```

### Phase 6 — Agent Workflow

加入：

```text
LangGraph
Workflow
Planning
Memory
Checkpoint
Human-in-the-loop
```

### Phase 7 — Evaluation Platform

把之前分散的 Evaluation 能力整合为平台：

```text
Eval Dataset
Eval Runner
Model Comparison
RAG Evaluation
Agent Evaluation
Regression Evaluation
Dashboard
```

### Phase 8 — Scaling & Engineering Expansion

只有真实需求出现后再进入：

```text
Redis
Qdrant
vLLM
Advanced Cache
Background Task Queue
Go Gateway
Distributed Service
Deployment Optimization
```

## 24. Go / Rust 定位

第一阶段不使用。

后期如果出现：

```text
高并发 Gateway
Streaming Service
独立基础设施服务
```

可以尝试：

```text
Python AI Core
        │
        ▼
Go Gateway
```

Go / Rust 是：

> 后期工程重构和性能实验方向，而不是初始依赖。

## 25. 项目成功标准

AetherLab 的成功不以“目录多”或“功能列表长”为标准。

真正的衡量标准是：

```text
能运行
能测试
能观测
能评测
能解释
能演示
能扩展
```

每一个阶段都应该产生一个真正可运行的纵向闭环。

最终 AetherLab 应成为：

> **一个能够真实展示 AI Engineering 能力，而不是停留在架构设计层面的完整工程项目。**
