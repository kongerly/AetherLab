# AetherLab 项目设计文档

## 1. 项目概述

### 1.1 项目名称

**AetherLab**

仓库名称：

```text
AetherLab
```

项目定位描述：

> A modular AI Engineering platform for LLM inference, RAG, Agents, evaluation and observability.

---

### 1.2 项目定位

AetherLab 是一个面向 AI Engineering 的模块化实验与应用平台，围绕大语言模型构建统一的：

- 模型接入
- 本地推理
- RAG
- Agent
- Tool Calling
- Memory
- Evaluation
- Observability
- 数据持久化
- Web 可视化

项目并不是一个单纯的聊天机器人，也不是简单封装第三方大模型 API，而是希望完成一套具有完整工程链路的 AI 应用系统。

项目核心定位：

> **以 AI / LLM 为核心，以 Backend 和 AI Engineering 为主要工程能力，以 Web 前端作为交互、调试和观测工具。**

整体重点：

```text
AI / LLM              ★★★★★
AI Engineering        ★★★★★
Backend Engineering   ★★★★☆
Data / Infra          ★★★☆☆
Frontend              ★★☆☆☆
DevOps                ★★☆☆☆
```

目标是：

> **AI Engineer 会做的全栈，而不是 Full-stack Engineer 顺便调用 LLM。**

---

## 2. 项目目标

### 2.1 核心目标

AetherLab 最终应支持：

1. 与不同 LLM 进行统一对话
2. 接入本地模型和云端模型
3. 使用 llama.cpp 运行 GGUF 本地模型
4. 管理模型配置
5. 创建和管理知识库
6. 文档解析、切分和向量化
7. 基于知识库进行 RAG 问答
8. 实现 Hybrid Retrieval 与 Reranker
9. 实现 Agent 与工具调用
10. 保存 Conversation 和 Message
11. 支持 Short-Term / Long-Term Memory
12. 查看模型调用过程
13. 查看 Retrieval / Rerank / Tool / Agent Trace
14. 对 Model / RAG / Agent 进行评测
15. 对性能和评测结果进行可视化
16. 使用 Docker 进行工程化部署

---

### 2.2 工程目标

项目需要体现：

- 清晰的模块划分
- 可替换的 LLM Provider
- 可替换的 Embedding Provider
- 可扩展 Tool System
- 可扩展 RAG Pipeline
- 数据持久化
- 异步调用
- 流式响应
- REST API
- SSE
- 统一配置管理
- 统一错误处理
- Logging
- Trace
- 自动化测试
- Docker
- CI
- 基础前端工程化

---

### 2.3 非目标

项目初期不追求：

- 从零训练大型语言模型
- 自研推理引擎
- 自研向量数据库
- 超高并发
- 分布式训练
- 微服务化
- Kubernetes
- 复杂商业级前端
- 重度 UI / 动画
- 过早使用 Go / Rust 重写核心系统

原则：

> 先完成一个结构清晰、可运行、可观测、可评测的 AI Engineering 系统，再逐步扩展。

---

## 3. 总体系统架构

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

---

## 4. 技术栈

### 4.1 核心语言

```text
Python
TypeScript
SQL
```

Python 负责：

- LLM
- RAG
- Agent
- Evaluation
- Backend
- Data Pipeline

TypeScript 负责前端。

SQL 负责关系型数据设计与查询。

---

### 4.2 AI / ML

```text
PyTorch
Transformers
Hugging Face
Sentence Transformers
PEFT
```

---

### 4.3 LLM Runtime

初期：

```text
llama.cpp
OpenAI Compatible API
```

可选：

```text
Ollama
```

后期：

```text
vLLM
```

---

### 4.4 Backend

```text
FastAPI
Pydantic
SQLAlchemy
Alembic
asyncio
pytest
```

---

### 4.5 Database

初期：

```text
PostgreSQL
pgvector
```

后期根据需求增加：

```text
Redis
Qdrant
```

---

### 4.6 Agent

```text
Custom Tool Calling Agent
LangGraph
```

原则：

> 先自己实现基础 Agent Loop，再使用 LangGraph 管理复杂 Workflow。

---

### 4.7 Frontend

```text
React
TypeScript
Vite
```

必要时增加：

```text
React Router
TanStack Query
Zustand
ECharts
```

前端定位：

> AI 系统的交互界面、Debug Console 和 Evaluation Dashboard。

---

### 4.8 Engineering

```text
Git
GitHub
Linux
Docker
Docker Compose
pytest
GitHub Actions
```

---

## 5. LLM 模型层设计

### 5.1 设计目标

所有上层业务逻辑不直接依赖具体模型实现。

统一抽象：

```python
class LLMProvider:
    async def generate(...):
        ...

    async def chat(...):
        ...

    async def stream(...):
        ...
```

实现：

```text
LLMProvider
├── LlamaCppProvider
├── OpenAIProvider
├── OllamaProvider
└── VLLMProvider
```

---

### 5.2 Provider Registry

后续可加入：

```text
LLMRegistry
```

负责：

```text
register()
get()
list()
health_check()
```

---

### 5.3 模型配置

模型配置可包含：

```text
id
name
provider
model_name
base_url
context_length
temperature
top_p
max_tokens
enabled
created_at
updated_at
```

敏感字段如 API Key 不得直接返回给前端。

---

## 6. llama.cpp 集成设计

本地模型不嵌入 FastAPI 进程。

推荐结构：

```text
GGUF Model
    │
    ▼
llama-server
    │
    ▼
OpenAI Compatible API
    │
    ▼
AetherLab Backend
```

AetherLab 与 llama.cpp 通过 HTTP 解耦。

这样可以：

- 独立启动或关闭模型
- 更换不同 GGUF 模型
- 使用不同 llama.cpp 参数
- 独立 Benchmark
- 不污染 Backend 进程

---

### 6.1 社区 Web UI

社区已有的 llama.cpp Web UI 可以继续使用。

结构：

```text
                 llama.cpp
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
AetherLab Backend          Community Web UI
```

社区 Web UI 用于：

- 快速测试模型
- Prompt 测试
- Sampling 参数测试
- 临时模型对比

AetherLab 自己的前端用于：

- RAG
- Agent
- Evaluation
- Trace
- Knowledge Base
- Model Management
- 系统级调试

二者定位不同，不冲突。

---

## 7. Conversation 模块

主要实体：

```text
Conversation
Message
Model
```

Conversation：

```text
id
title
model_id
created_at
updated_at
```

Message：

```text
id
conversation_id
role
content
token_count
latency
metadata
created_at
```

---

### 7.1 对话流程

```text
User Message
      │
      ▼
API Route
      │
      ▼
ChatService
      │
      ├── Save User Message
      │
      ▼
LLM Provider
      │
      ▼
Streaming Response
      │
      ├── SSE → Frontend
      │
      └── Save Assistant Message
```

流式输出第一阶段优先：

```text
SSE
```

只有未来出现复杂双向实时通信时才考虑 WebSocket。

---

## 8. RAG 系统设计

### 8.1 文档处理流程

```text
Document
   │
   ▼
Parser
   │
   ▼
Cleaner
   │
   ▼
Chunker
   │
   ▼
Embedding
   │
   ▼
Vector Store
```

---

### 8.2 查询流程

```text
Query
  │
  ▼
Embedding
  │
  ▼
Retriever
  │
  ▼
Candidate Chunks
  │
  ▼
Reranker
  │
  ▼
Context Builder
  │
  ▼
LLM
  │
  ▼
Answer + Citation
```

---

### 8.3 Knowledge Base

```text
KnowledgeBase
├── id
├── name
├── description
├── embedding_model
├── chunk_strategy
├── created_at
└── updated_at
```

---

### 8.4 Document

```text
Document
├── id
├── knowledge_base_id
├── filename
├── file_type
├── file_size
├── status
├── checksum
├── metadata
└── created_at
```

状态：

```text
uploaded
processing
completed
failed
```

---

### 8.5 Chunk

```text
Chunk
├── id
├── document_id
├── content
├── chunk_index
├── token_count
├── metadata
└── embedding
```

---

### 8.6 Chunking

第一阶段：

```text
Recursive Character Split
```

后续：

```text
Token-based Chunking
Sentence Chunking
Markdown-aware Chunking
Semantic Chunking
```

支持：

```text
chunk_size
chunk_overlap
```

---

### 8.7 Retrieval

第一阶段：

```text
Vector Search
```

第二阶段：

```text
Vector Search
+
BM25
```

形成：

```text
Query
 ├──── Vector Retriever
 │
 └──── BM25 Retriever
          │
          ▼
       Fusion
          │
          ▼
       Reranker
          │
          ▼
       Top Context
```

---

### 8.8 Reranker

目标流程：

```text
Recall Top 30
       │
       ▼
    Reranker
       │
       ▼
     Top 5
       │
       ▼
      LLM
```

可使用 Cross Encoder 或其他 Reranker。

---

## 9. Agent 系统设计

### 9.1 基础 Agent Loop

```text
User
 │
 ▼
Agent
 │
 ▼
LLM
 │
 ├── Final Answer
 │
 └── Tool Call
        │
        ▼
       Tool
        │
        ▼
    Observation
        │
        └──────► LLM
```

---

### 9.2 Agent State

```text
AgentState
├── messages
├── tool_calls
├── tool_results
├── context
├── memory
├── current_step
└── metadata
```

---

### 9.3 执行限制

必须支持：

```text
max_steps
max_tool_calls
timeout
retry
fallback
error_handling
```

避免 Agent 无限循环。

---

### 9.4 Workflow

第一阶段：

```text
Custom Agent Loop
```

第二阶段：

```text
LangGraph
```

支持：

```text
State
Node
Edge
Conditional Edge
Checkpoint
Human-in-the-loop
```

---

## 10. Tool System

统一接口：

```python
class Tool:
    name: str
    description: str
    input_schema: dict

    async def execute(self, arguments):
        ...
```

第一阶段：

```text
CalculatorTool
DateTimeTool
RAGTool
```

后续：

```text
SearchTool
DatabaseTool
PythonTool
FileTool
HTTPTool
```

---

### 10.1 Tool Registry

```text
ToolRegistry
├── register()
├── get()
├── list()
└── execute()
```

Agent 不直接创建 Tool。

---

## 11. Memory 系统

### 11.1 Short-Term Memory

当前 Conversation Context。

策略：

```text
message history
truncate
summary
```

---

### 11.2 Long-Term Memory

后期加入：

```text
User Preference
Important Fact
Previous Task
Project Context
```

使用 Embedding Retrieval 召回。

---

## 12. Evaluation 系统

项目必须能够回答：

> 修改了模型、Prompt、Retriever、Reranker 或 Agent 以后，到底变好了还是变差了？

---

### 12.1 Model Evaluation

记录：

```text
TTFT
Total Latency
Tokens / Second
Prompt Tokens
Completion Tokens
Total Tokens
```

本地模型额外记录：

```text
Model
Quantization
Context Size
GPU Layers
Memory Usage
```

---

### 12.2 RAG Evaluation

```text
Retrieval Recall
MRR
Hit Rate
Context Precision
Context Recall
Answer Correctness
Faithfulness
```

---

### 12.3 Agent Evaluation

```text
Task Success
Tool Selection Accuracy
Tool Call Count
Step Count
Failure Rate
Latency
Token Usage
```

---

### 12.4 Eval Dataset

```text
EvalDataset
├── id
├── name
├── type
└── description
```

```text
EvalCase
├── input
├── expected_output
├── expected_context
├── metadata
└── tags
```

每次执行生成：

```text
EvalRun
```

---

## 13. Trace / Observability

每次 AI 请求产生一个 Trace。

```text
Trace
 │
 ├── LLM Call
 ├── Retrieval
 ├── Rerank
 ├── Tool Call
 └── Agent Step
```

记录：

```text
trace_id
request_id
conversation_id
model
prompt_tokens
completion_tokens
latency
status
error
created_at
```

---

### 13.1 Agent Trace

前端示例：

```text
Agent Run #42

Step 1
LLM → Search Tool

Step 2
Search → Result

Step 3
LLM → RAG Tool

Step 4
RAG → 5 Chunks

Step 5
LLM → Final Answer
```

Trace 同时承担：

```text
Debug
Evaluation
Demo
```

---

## 14. 数据库设计

核心数据库：

```text
PostgreSQL
```

向量：

```text
pgvector
```

核心表规划：

```text
users

models

conversations
messages

knowledge_bases
documents
chunks

agents
agent_runs
agent_steps

tools
tool_calls

eval_datasets
eval_cases
eval_runs
eval_results

traces
```

第一阶段使用 PostgreSQL + pgvector，避免过早引入独立 Vector Database。

后期再根据数据规模评估：

```text
Qdrant
Milvus
```

---

## 15. Redis

Redis 第一阶段不是强制依赖。

后续可用于：

```text
Cache
Rate Limit
Session
Task State
Queue
Distributed Lock
```

只有出现真实需求后再引入。

---

## 16. 后端架构

Backend 作为独立 Python Project。

推荐结构：

```text
backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── llm/
│   ├── rag/
│   ├── agent/
│   ├── eval/
│   ├── observability/
│   └── main.py
│
├── tests/
└── pyproject.toml
```

其中：

```text
backend
```

是独立 Python 项目。

```text
app
```

是主要 Python package。

因此 import 推荐：

```python
from app.core.config import settings
from app.llm.base import LLMProvider
from app.services.chat import ChatService
```

---

## 17. Backend 分层设计

### 17.1 API Layer

负责：

```text
参数解析
参数校验
鉴权
调用 Service
返回 Response
```

不得堆积复杂业务逻辑。

---

### 17.2 Service Layer

例如：

```text
ChatService
RAGService
AgentService
KnowledgeService
ModelService
EvalService
```

负责业务流程编排。

---

### 17.3 Repository Layer

负责数据库访问。

```text
ConversationRepository
MessageRepository
DocumentRepository
ModelRepository
```

---

### 17.4 Models

数据库 ORM Model。

例如：

```python
class Conversation(Base):
    ...
```

---

### 17.5 Schemas

Pydantic API 数据结构。

例如：

```python
class ConversationCreate(BaseModel):
    title: str
```

---

### 17.6 分层关系

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

---

## 18. API 初步设计

### Chat

```text
POST   /api/v1/chat
POST   /api/v1/chat/stream
```

### Conversation

```text
GET    /api/v1/conversations
POST   /api/v1/conversations
GET    /api/v1/conversations/{id}
DELETE /api/v1/conversations/{id}
GET    /api/v1/conversations/{id}/messages
```

### Model

```text
GET    /api/v1/models
POST   /api/v1/models
PATCH  /api/v1/models/{id}
DELETE /api/v1/models/{id}
POST   /api/v1/models/{id}/test
```

### Knowledge Base

```text
GET    /api/v1/knowledge-bases
POST   /api/v1/knowledge-bases
GET    /api/v1/knowledge-bases/{id}
DELETE /api/v1/knowledge-bases/{id}
```

### Document

```text
POST   /api/v1/knowledge-bases/{id}/documents
GET    /api/v1/documents/{id}
DELETE /api/v1/documents/{id}
```

### RAG

```text
POST   /api/v1/rag/retrieve
POST   /api/v1/rag/query
```

### Agent

```text
GET    /api/v1/agents
POST   /api/v1/agents
POST   /api/v1/agents/{id}/run
GET    /api/v1/agent-runs/{id}
```

### Evaluation

```text
POST   /api/v1/evals
POST   /api/v1/evals/{id}/run
GET    /api/v1/eval-runs
GET    /api/v1/eval-runs/{id}
```

### Health

第一阶段首先实现：

```text
GET /health
```

返回：

```json
{
  "status": "ok",
  "service": "aetherlab"
}
```

---

## 19. 前端设计

前端页面规划：

```text
/
├── Chat
├── Knowledge
├── Models
├── Agents
├── Evaluation
├── Traces
└── Settings
```

---

### 19.1 Chat

支持：

```text
Conversation List
Model Select
Knowledge Base Select
Agent Mode
Streaming
Markdown
Code Block
Citation
```

---

### 19.2 Knowledge

展示：

```text
Knowledge Base
Documents
Processing Status
Chunks
Retrieval Test
```

用于直接调试 RAG。

---

### 19.3 Models

展示：

```text
Model Name
Provider
Context
Status
Latency
Tokens/s
```

支持：

```text
Add Model
Test Model
Disable Model
```

---

### 19.4 Agents

展示完整 Agent Run 和 Tool Calling 过程。

---

### 19.5 Evaluation

用于：

```text
Model Comparison
RAG Evaluation
Agent Evaluation
Benchmark Result
```

---

### 19.6 Traces

用于查看：

```text
LLM Call
Retrieval
Reranker
Tool Call
Agent Step
Latency
Token Usage
Error
```

---

## 20. 项目目录结构

### 20.1 当前推荐结构

```text
AetherLab/
│
├── backend/
│   │
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   └── main.py
│   │
│   ├── tests/
│   └── pyproject.toml
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
├── .gitignore
├── .env.example
├── docker-compose.yml
├── README.md
└── LICENSE
```

项目初期不需要把所有未来模块的空文件全部创建出来。

随着开发逐步增加：

```text
开始数据库
→ app/db/

开始 LLM Provider
→ app/llm/

开始 RAG
→ app/rag/

开始 Agent
→ app/agent/

开始 Eval
→ app/eval/

开始 Trace
→ app/observability/
```

原则：

> 目录跟着真实代码增长，而不是提前制造大量空结构。

---

## 21. 最终目标目录结构

```text
AetherLab/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── chat.py
│   │   │   │   ├── models.py
│   │   │   │   ├── knowledge.py
│   │   │   │   ├── agents.py
│   │   │   │   └── evals.py
│   │   │   └── dependencies.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   └── exceptions.py
│   │   │
│   │   ├── db/
│   │   │   ├── session.py
│   │   │   ├── base.py
│   │   │   └── migrations/
│   │   │
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   │
│   │   ├── llm/
│   │   │   ├── base.py
│   │   │   ├── registry.py
│   │   │   ├── types.py
│   │   │   └── providers/
│   │   │       ├── llama_cpp.py
│   │   │       ├── openai.py
│   │   │       ├── ollama.py
│   │   │       └── vllm.py
│   │   │
│   │   ├── rag/
│   │   │   ├── parsers/
│   │   │   ├── chunkers/
│   │   │   ├── embeddings/
│   │   │   ├── retrievers/
│   │   │   └── rerankers/
│   │   │
│   │   ├── agent/
│   │   │   ├── tools/
│   │   │   ├── executor.py
│   │   │   └── state.py
│   │   │
│   │   ├── eval/
│   │   ├── observability/
│   │   └── main.py
│   │
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   │
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── stores/
│   │   ├── types/
│   │   └── App.tsx
│   │
│   ├── package.json
│   └── vite.config.ts
│
├── docs/
│   ├── design.md
│   ├── architecture.md
│   ├── api.md
│   ├── database.md
│   ├── rag.md
│   ├── agent.md
│   └── roadmap.md
│
├── scripts/
├── data/
│   └── .gitkeep
├── docker/
├── .github/
│   └── workflows/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
├── LICENSE
└── CONTRIBUTING.md
```

---

## 22. 配置设计

真实环境配置：

```text
.env
```

示例配置：

```text
.env.example
```

例如：

```dotenv
DATABASE_URL=
REDIS_URL=
LLAMA_CPP_BASE_URL=http://localhost:8080
OPENAI_API_KEY=
LOG_LEVEL=INFO
UPLOAD_DIR=
```

禁止提交：

```text
API Key
Password
Secret
Token
Cookie
Private Endpoint Credential
```

---

## 23. GitHub 与公开策略

AetherLab 采用公开仓库。

建议公开：

```text
README.md
LICENSE
.env.example
.gitignore
docker-compose.yml
backend/
frontend/
docs/
GitHub Actions
公开测试代码
公开示例数据
```

不应公开：

```text
.env
真实 API Key
数据库密码
Token
Cookie
个人数据
真实用户数据
本地模型文件
大量测试数据
日志
缓存
虚拟环境
node_modules
```

---

### 23.1 `.gitignore`

建议：

```gitignore
# Environment
.env
.env.*
!.env.example

# Python
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Virtual environments
.venv/
venv/

# IDE
.idea/
.vscode/

# Node
node_modules/
frontend/dist/

# Data
data/*
!data/.gitkeep

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Secrets
*.pem
*.key

# Database
*.db
*.sqlite
*.sqlite3
```

重要：

> 已经 commit 过的敏感信息不会因为后来加入 `.gitignore` 而自动从 Git 历史中消失。

因此 Secret 从第一次提交开始就不得进入 Git。

---

## 24. 文档与语言规范

推荐：

```text
代码                         英文
变量 / 函数 / 类名            英文
文件名                       英文
代码注释                     英文
Commit Message              英文
API / Log / Error Message   英文
README.md                   英文为主
docs/design.md              中文
个人设计和学习文档             中文
```

原因：

- 代码与主流开源生态保持一致
- 方便搜索错误
- 方便未来展示
- 设计文档使用中文可以提高思考和维护效率

---

## 25. README 与 Design 文档定位

### README.md

面向第一次访问仓库的人。

主要包含：

```text
项目介绍
核心特性
架构概览
Quick Start
Roadmap
Documentation
```

---

### docs/design.md

面向项目开发。

包含：

```text
系统架构
技术选型
模块划分
数据库设计
API
RAG
Agent
Evaluation
Observability
开发阶段
```

设计文档建议公开，并与代码一起进行版本管理。

---

## 26. Logging

统一结构化 Logging。

等级：

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

记录：

```text
request_id
trace_id
model
latency
tokens
status
error
```

---

## 27. Error Handling

统一 API Error：

```json
{
  "code": "MODEL_UNAVAILABLE",
  "message": "Model service unavailable",
  "request_id": "xxx"
}
```

禁止：

```python
try:
    ...
except:
    pass
```

错误应该：

```text
分类
记录
传播
转换
返回
```

---

## 28. Testing

分为：

```text
Unit Test
Integration Test
Evaluation Test
```

Unit Test：

```text
Chunker
Retriever
Tool
Prompt Builder
Parser
```

Integration Test：

```text
API
Database
LLM Provider
RAG Pipeline
Agent
```

Evaluation Test：

```text
RAG Recall
Agent Success Rate
Regression Evaluation
```

---

## 29. Docker

最终使用：

```text
Docker Compose
```

结构：

```text
docker-compose
├── backend
├── frontend
├── postgres
├── redis
└── optional services
```

llama.cpp 可以独立运行。

原因：

- GPU Runtime 环境独立
- 本地推理参数变化频繁
- 与 Backend 解耦更清晰

---

## 30. 项目开发阶段

### Phase 0：Project Bootstrap

完成：

```text
Git Repository
GitHub Repository
Basic Directory Structure
.gitignore
README
Design Document
Python Environment
FastAPI
GET /health
```

第一版目标：

```text
GET /health
```

返回：

```json
{
  "status": "ok",
  "service": "aetherlab"
}
```

---

### Phase 1：LLM Chat

```text
LLM Provider
llama.cpp
Cloud API
Conversation
Message
Streaming
Chat UI
```

---

### Phase 2：RAG

```text
Knowledge Base
Document Upload
Parser
Chunker
Embedding
Vector Search
RAG
Citation
Retrieval Debug UI
```

---

### Phase 3：Advanced RAG

```text
BM25
Hybrid Search
Reranker
Query Rewrite
RAG Evaluation
```

---

### Phase 4：Agent

```text
Tool Calling
Tool Registry
Agent Loop
Agent State
Agent Trace
```

---

### Phase 5：Agent Workflow

```text
LangGraph
Workflow
Planning
Memory
Checkpoint
```

---

### Phase 6：Evaluation

```text
Eval Dataset
Eval Runner
Model Eval
RAG Eval
Agent Eval
Comparison Dashboard
```

---

### Phase 7：Observability

```text
Trace
Metrics
Token Usage
Latency
Error Analysis
Dashboard
```

---

### Phase 8：Engineering

```text
Docker
CI
Test
Security
Configuration
Documentation
Deployment
```

---

## 31. Go / Rust 的定位

第一阶段不使用。

主要延迟通常来自：

```text
Model Inference
Network
Vector Search
Database
```

而不是 Python 本身。

后期可以把项目演化成：

```text
Python AI Core
        │
        ▼
Go Gateway
```

或者使用 Go 重写：

```text
API Gateway
Concurrent Service
Streaming Service
```

Go / Rust 的定位是：

> 后期工程重构与性能实验，而不是项目初始依赖。

---

## 32. 项目设计原则

### 32.1 AI First

核心始终是：

```text
LLM
RAG
Agent
Evaluation
Observability
```

---

### 32.2 Understand Before Framework

先自己实现基础能力，再使用框架。

```text
Retriever
RAG
Tool Calling
Agent Loop
```

理解之后再引入：

```text
LangGraph
其他高层框架
```

---

### 32.3 Observable

不能只得到：

```text
Answer
```

还要能够知道：

```text
使用了哪个模型
检索了什么
Reranker 如何排序
调用了什么 Tool
Agent 走了哪些 Step
耗时是多少
Token 使用多少
哪里失败了
```

---

### 32.4 Evaluatable

任何 AI 模块修改后，都应能够量化比较。

---

### 32.5 Replaceable

关键组件应尽量可替换：

```text
LLM
Embedding
Retriever
Reranker
Vector Store
Tool
```

---

### 32.6 Incremental

演化顺序：

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

---

## 33. 项目最终形态

```text
                       AetherLab

┌─────────────────────────────────────────────────────────┐
│                         Web UI                          │
│                                                       │
│ Chat │ Knowledge │ Agent │ Evaluation │ Trace │ Model │
└────────────────────────────┬────────────────────────────┘
                             │
                          FastAPI
                             │
       ┌─────────────────────┼─────────────────────┐
       │                     │                     │
       ▼                     ▼                     ▼
     LLM                   RAG                   Agent
       │                     │                     │
       │              ┌──────┼───────┐            │
       │              │      │       │            │
       │           Vector   BM25  Reranker        Tool
       │                                          │
       └──────────────────┬───────────────────────┘
                          │
                         Eval
                          │
                         Trace
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
      PostgreSQL        pgvector         Redis
```

AetherLab 最终应同时体现：

### AI 原理能力

```text
Transformer
Embedding
RAG
Agent
LLM Inference
```

### AI Engineering 能力

```text
LLM Integration
RAG Pipeline
Agent Workflow
Evaluation
Observability
```

### Software Engineering 能力

```text
Backend
Database
API
Async
Testing
Docker
Frontend
Git / GitHub
```

最终目标不是一个普通的：

> “LLM 聊天网站”

而是一个：

> **可运行、可扩展、可调试、可评测、可展示的 AI Engineering Platform。**
