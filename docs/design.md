# AetherLab 项目设计

本文档只记录相对稳定的项目定位、设计原则、总体架构与技术方向。

频繁变化的进度与阶段目标见 [`roadmap.md`](roadmap.md)，后端实现约束见
[`backend.md`](backend.md)，工程规范见 [`engineering.md`](engineering.md)。

## 1. 项目定位

**AetherLab** 是一个面向 AI Engineering 的模块化实验与应用平台，围绕大语言模型构建统一的：

- LLM Provider
- Local / Cloud Inference
- Chat
- RAG
- Agent 与 Tool Calling
- Memory
- Evaluation
- Observability
- Persistence
- Web UI

它不是简单的聊天机器人，也不是对单一模型 API 的薄封装。项目目标是形成一个：

> 可运行、可扩展、可替换、可调试、可观测、可评测的 AI Engineering Platform。

## 2. 核心原则

### 2.1 AI First

项目核心始终围绕 LLM、RAG、Agent、Evaluation 与 Observability。前端、数据库和部署能力
服务于 AI 系统，不让项目演化成与目标无关的通用 CRUD 系统。

### 2.2 Vertical Slice First

优先完成小而完整的纵向闭环，而不是同时铺开大量不具备实际行为的模块。

第一条目标链路是：

```text
OpenAI-compatible Provider
↓
Chat API
↓
SSE Streaming
↓
Minimal Frontend
↓
Trace
↓
Tests
```

### 2.3 Understand Before Framework

先理解并实现 Provider abstraction、Retriever、RAG pipeline、Tool calling 和 Agent loop 的
基础版本，再根据真实复杂度引入 LangGraph 或高级 RAG 框架。

### 2.4 Observable From Day One

从第一条 LLM 调用链开始记录 Provider、Model、Latency、Status、Error、Token Usage、
Request ID 与 Trace ID。随着功能增长，再扩展到 Retrieval、Rerank、Tool Call 和 Agent Step。

### 2.5 Test Early

测试与功能一起增长。每完成一个纵向功能，就增加能保护其外部行为的测试，而不是在项目后期
集中补测试。

### 2.6 Evaluatable

重要 AI 模块的变更必须能够回答“变好了还是变差了”。Prompt、Model Config、Retriever
Config、Eval Dataset 等对象后续需要具备版本概念，确保结果可比较、可复现。

### 2.7 Replaceable

LLM、Embedding、Retriever、Reranker、Vector Store 和 Tool 等关键组件通过清晰接口解耦，
业务层不依赖单一供应商或运行时。

### 2.8 Incremental

项目按以下顺序演化：

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

仅在真实需求出现后增加复杂度。

## 3. 总体架构愿景

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
│ metadata     │ │ embedding    │ │  optional   │
└──────────────┘ └──────────────┘ └─────────────┘
```

该图描述最终架构愿景，不表示所有组件已经实现。当前实现状态与各阶段完成条件以
[`roadmap.md`](roadmap.md) 为准。

### 3.1 分层关系

```text
Web UI
  │
  ▼
API Route
  │
  ▼
Service
  │
  ├── LLM / RAG / Agent / Eval
  │
  ▼
Repository
  │
  ▼
Database / Model Runtime
```

- API 层负责协议、校验与响应，不堆积复杂业务逻辑。
- Service 层编排业务流程。
- Repository 层隔离持久化实现。
- Provider 与 Tool 接口隔离外部能力。
- Observability 横跨所有层，而不是独立追加在最后。

## 4. 技术方向

技术选型按阶段引入。以下列表包含当前技术与已确定的目标方向，并不等于已经安装或实现。

### 4.1 核心语言

- Python
- TypeScript
- SQL

### 4.2 Backend

- Python 3.13
- FastAPI
- Pydantic
- asyncio
- SQLAlchemy 与 Alembic（持久化阶段）
- pytest
- Ruff
- uv

### 4.3 AI / ML

- PyTorch
- Transformers
- Hugging Face
- Sentence Transformers
- PEFT

这些依赖只在对应功能进入实现阶段后加入。

### 4.4 LLM Runtime

初期以 OpenAI-compatible API 和 llama.cpp 为主，可按需求接入云服务或 Ollama；vLLM 留到
真实吞吐量需求出现后评估。

### 4.5 Data Infrastructure

初期持久化方向为 PostgreSQL 与 pgvector。Redis、Qdrant 和后台任务系统只有在缓存、队列或
检索需求明确后再引入。

### 4.6 Frontend

前端方向为 React、TypeScript 与 Vite。React Router、TanStack Query、Zustand、ECharts 等
库根据界面复杂度逐步选择，不作为初始依赖。

### 4.7 Engineering

- Git 与 GitHub
- Docker 与 Docker Compose
- GitHub Actions
- VS Code

### 4.8 Go / Rust 的定位

第一阶段不使用 Go 或 Rust。后期只有出现高并发 Gateway、独立 Streaming Service 或明确的
性能瓶颈时，才考虑将部分基础设施从 Python AI Core 中拆出。

## 5. 最终目标

AetherLab 的成功不以目录数量或功能列表长度衡量，而以每个阶段是否真正做到以下几点衡量：

```text
能运行
能测试
能观测
能评测
能解释
能演示
能扩展
```

最终，AetherLab 应成为一个能够真实展示 AI Engineering 能力，而不是停留在架构设计层面的
完整工程项目。
