# AetherLab 工程规范

本文档记录仓库结构、开发工作流、代码质量、测试、CI、安全与公开策略。

项目定位见 [`design.md`](design.md)，阶段进度见 [`roadmap.md`](roadmap.md)，后端内部设计见
[`backend.md`](backend.md)。AI coding agent 还必须遵守仓库根目录的 [`AGENTS.md`](../AGENTS.md)。

## 1. 仓库结构

当前推荐结构：

```text
AetherLab/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/routes/health.py
│   │   └── core/              # Config, errors, JSON logging, request middleware
│   ├── tests/
│   ├── .env.example
│   ├── .python-version
│   ├── pyproject.toml
│   └── uv.lock
├── frontend/
├── docs/
│   ├── design.md
│   ├── roadmap.md
│   ├── backend.md
│   └── engineering.md
├── scripts/
├── data/
│   └── .gitkeep
├── .github/
│   └── workflows/
├── .vscode/
│   ├── extensions.json
│   ├── launch.json
│   └── settings.json
├── .env.example
├── .editorconfig
├── .gitattributes
├── .gitignore
├── AGENTS.md
├── docker-compose.yml
├── README.md
└── LICENSE
```

原则：

- 不提前创建大量空模块。
- 新目录必须对应正在实现的功能。
- 生成文件、缓存、虚拟环境和本地数据不得提交。
- 根目录保留跨项目组件的入口与说明，详细设计放在 `docs/`。

## 2. 本地开发工作流

后端命令从 `backend/` 执行：

```bash
uv sync --frozen
uv run uvicorn app.main:app --reload --no-access-log
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

配置模板在 `backend/.env.example`，可选复制为同目录 `.env`。关闭 Uvicorn access log，
由应用 JSON 日志记录路由模板，避免原始 URL 中的敏感内容进入日志。

开发者应使用 `uv.lock` 中锁定的版本。修改依赖时同时更新 `pyproject.toml` 与 `uv.lock`，并在
提交中说明新增生产依赖的用途。

## 3. 代码与文档语言

| 内容 | 语言 |
| --- | --- |
| 代码、变量、函数、类和文件名 | 英文 |
| 正式注释与 Docstring 说明 | 优先中文，Google 风格的 `Args:`、`Returns:`、`Raises:` 等标签保留英文 |
| Commit Message | 中文或英文，清楚表达变更目的 |
| API、Log 与 Error Message | 英文 |
| `README.md` | 中文为主，按需保留英文简介与技术术语 |
| `docs/*.md` | 中文为主，保留必要的英文技术术语 |
| 开发临时注释 | 可使用中文，提交前整理 |

需要长期保留的注释应简洁说明设计原因、边界条件和取舍，不重复代码已经表达的行为。
中文注释可以直接提交，无需翻译成英文。类型注解和代码标识符仍使用原有 Python 语法与英文命名。

## 4. Python 规范

### 4.1 命名

```text
文件名          snake_case.py
变量            snake_case
函数            snake_case
类              PascalCase
常量            UPPER_SNAKE_CASE
私有成员        _leading_underscore
```

### 4.2 基本要求

- 使用 Python 3.13，并遵守 `backend/pyproject.toml` 的版本范围。
- 公共接口与非简单内部函数使用类型注解。
- 公共函数和类使用 Google 风格 Docstring。
- Docstring 说明优先中文，结构标签保留英文，首句使用完整的句末标点。
  Ruff 的 D415 不识别中文句末标点，因此禁用该项并由人工检查，其余文档字符串规则保留。
- Ruff 是格式化、导入排序和静态检查的唯一配置来源。
- 避免在同一提交中进行与功能无关的大规模重构。
- 不使用注释关闭规则来掩盖可以直接修复的问题。

## 5. Testing

测试随纵向功能一起增加，不留到项目最后。

测试类型按需包括：

- Unit Test：纯业务逻辑、解析、策略和边界条件
- API Test：路由、状态码、Schema 与错误结构
- Integration Test：Provider、数据库与跨层行为
- Evaluation Test：RAG、Agent 和模型行为的质量回归

实施顺序：

```text
Health Endpoint → API Test
Provider        → Provider Unit / Contract Test
Chat            → Chat Integration Test
RAG             → Retrieval Evaluation
Agent           → Tool and Task Evaluation
```

测试要求：

- 验证外部可观察行为，不机械复制实现。
- 默认不依赖真实付费 API、个人密钥或不稳定外部服务。
- 需要外部服务的测试必须可显式选择，并提供清楚的跳过条件。
- Bug 修复应在可行时先添加能复现问题的测试。
- 不用提高覆盖率数字代替有意义的断言。

## 6. Continuous Integration

当前 `.github/workflows/backend-ci.yml` 在 push 与 pull request 修改 `backend/**`
或该工作流时执行，使用 Python 3.13，并设置 `APP_ENV=test`、`LOG_LEVEL=INFO`：

```text
uv sync --frozen
ruff check
ruff format --check
pytest
```

CI 使用锁文件、固定 Python 版本并缓存依赖。本地检查通过不等同于远端 CI 已通过，
阶段验收须核对 GitHub Actions 的实际运行结果。只有在基础流程稳定后，再添加集成测试、构建、
安全扫描或发布任务。

## 7. Git 与变更管理

- Commit Message 使用简洁的中文或英文并表达变更目的。
- 一个提交聚焦一个可解释的变更。
- 提交前检查 diff 中是否包含密钥、生成文件和无关修改。
- 不重写他人的提交或丢弃未确认的本地修改。
- 行为、配置、启动方式或目录结构变化时同步更新相关文档。
- 不提交仅适用于个人机器的路径、端口偏好或模型位置。

## 8. Security

第一阶段不实现复杂多租户系统，但从一开始遵守以下边界：

- API Key 不返回前端、不写入日志、不提交 Git。
- `.env`、Token、Password、Cookie、私钥和个人配置保持本地。
- 日志与 Trace 在记录 Prompt、Tool Arguments 和用户数据前必须有脱敏策略。
- 上传内容、检索内容和 Tool Output 都视为不可信输入。
- 文件上传需要大小、类型、路径和内容校验。
- Tool 系统需要明确权限边界、参数校验、超时和调用次数限制。
- Prompt injection 不得绕过数据访问或 Tool 权限。

## 9. 公开仓库策略

### 9.1 可以公开

- `README.md`、`LICENSE` 与项目文档
- `AGENTS.md` 中的项目级 AI 协作规范
- `.env.example` 中的安全占位符
- `.gitignore`、`.gitattributes` 与 `.editorconfig`
- Docker、CI 与共享 VS Code 配置
- 源码、测试和经过审查的示例数据

### 9.2 不得公开

- `.env`
- API Key、Password、Token、Cookie 与私钥
- 真实用户数据和未脱敏日志
- 本地模型文件与大型个人数据集
- `.venv`、`node_modules`、缓存和构建产物
- 私有端点、个人路径和机器专用 AI 指令

各级目录的 `AGENTS.override.md` 用于本机覆盖并由 `.gitignore` 忽略。它会替换同目录的
`AGENTS.md`，因此需要保留仍然适用的公共规则；机密信息仍应放在 `.env` 或密钥管理器中。
常见模型权重扩展名（`.gguf`、`.safetensors`、`.pt`、`.pth`、`.ckpt`）也由 `.gitignore`
忽略。忽略规则不能覆盖所有敏感文件格式，提交前仍须检查暂存区；已跟踪文件不会因新增规则而自动移除。

## 10. 文档职责

- `README.md`：面向新读者的项目介绍、当前能力和快速启动。
- `docs/design.md`：稳定的定位、原则、总体架构与技术方向。
- `docs/roadmap.md`：当前进度、Phase 计划和完成条件。
- `docs/backend.md`：后端分层、Provider、Chat、SSE、错误和日志设计。
- `docs/engineering.md`：开发流程、质量标准、CI、安全和公开策略。
- `AGENTS.md`：AI coding agent 可直接执行的项目级工作说明。

只有相关功能真正进入实现阶段后，才新增 `rag.md`、`agent.md`、`evaluation.md` 或
`observability.md`。不创建空的占位文档。

## 11. 完成检查

提交代码前确认：

1. 相关 Ruff、Format 与 Test 检查通过。
2. 新行为具备有意义的测试。
3. README、设计、路线图和实际实现没有相互矛盾。
4. Diff 不包含密钥、缓存、生成文件或无关修改。
5. 未执行的检查及原因在交付说明中明确列出。
