# 政务智能问答系统

本项目为四川农业大学 23 级实训项目方向一：智能体应用开发（政务智能问答系统）。系统面向政务服务咨询场景，计划通过政策知识库、RAG 检索增强和大模型 API，为用户提供政策解读、办事流程咨询、民生问题引导等智能问答能力。

本项目不开发方向二“政务瞭望系统”，不以爬虫、政务情报收集、多源信息采集或智能报告生成为核心功能。

## 技术栈规划

| 类型 | 技术 |
| --- | --- |
| 后端 | FastAPI |
| 前端 | Vue 3 |
| 数据库 | MySQL |
| 向量数据库 | Chroma |
| 大模型 API | DeepSeek 或通义千问，保留可配置接口 |
| 部署 | Docker，作为后续增强 |

## 当前项目目录结构

```text
.
├─ backend/
│  ├─ requirements.txt
│  ├─ Dockerfile
│  └─ app/
│     ├─ main.py
│     ├─ config.py
│     ├─ database.py
│     ├─ models/
│     ├─ schemas/
│     ├─ routers/
│     │  ├─ health.py
│     │  ├─ database.py
│     │  ├─ category.py
│     │  ├─ knowledge.py
│     │  ├─ chat.py
│     │  └─ safety.py
│     ├─ services/
│     └─ utils/
├─ frontend/
│  ├─ package.json
│  ├─ index.html
│  ├─ Dockerfile
│  └─ src/
│     ├─ main.js
│     ├─ App.vue
│     ├─ router/
│     ├─ pages/
│     ├─ components/
│     └─ api/
├─ data/
│  ├─ policies/
│  ├─ faq/
│  └─ samples/
├─ docs/
├─ scripts/
├─ .env.example
├─ .gitignore
├─ docker-compose.yml
├─ AGENTS.md
└─ README.md
```

## 后端最小启动方式

当前后端提供健康检查接口和基础数据库验证接口，不实现 RAG、大模型调用或正式问答逻辑。

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

启动后访问：

```text
GET http://localhost:8000/health
```

预期返回：

```json
{
  "status": "ok",
  "message": "政务智能问答系统后端服务运行正常"
}
```

## 数据库配置与初始化

### 1. 配置 `.env`

复制 [.env.example](D:/admin/Desktop/实训项目一/.env.example) 为 `.env`，并按本机 MySQL 情况修改配置：

```env
APP_NAME=政务智能问答系统
APP_ENV=development
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/gov_ai_assistant
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.example.com
VECTOR_DB_PATH=./data/vector_db
```

不要把真实数据库密码或 API Key 提交到仓库。

### 2. 创建 MySQL 数据库

在 MySQL 中先创建目标数据库：

```sql
CREATE DATABASE gov_ai_assistant
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
```

### 3. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

本阶段新增依赖包括 `sqlalchemy` 和 `pymysql`。

### 4. 初始化数据表

从项目根目录运行：

```bash
python scripts/init_db.py
```

成功后会输出：

```text
数据库表初始化完成
```

该脚本只创建表结构，不删除已有数据，也不会自动插入大量数据。

### 5. 验证数据库连接

启动后端后访问：

```text
GET http://localhost:8000/database/ping
```

预期返回：

```json
{
  "status": "ok",
  "message": "数据库连接正常"
}
```

查看已创建的主要表：

```text
GET http://localhost:8000/database/tables
```

主要表包括：

1. `users`
2. `categories`
3. `knowledge_docs`
4. `chat_records`
5. `feedback`

### 6. 在 DataGrip 中检查表结构

1. 新建 MySQL 数据源。
2. 填写主机、端口、用户名和密码。
3. 选择或刷新 `gov_ai_assistant` 数据库。
4. 展开 `tables`，确认 `users`、`categories`、`knowledge_docs`、`chat_records`、`feedback` 已创建。
5. 可查看每张表的字段、主键和外键关系。

## 知识库基础管理

当前知识库仍是普通 MySQL 数据库存储，只提供基础分类、知识文档 CRUD 和关键词 LIKE 搜索。RAG、向量检索、Chroma 和大模型调用将在后续步骤实现。

### 1. 初始化默认政务分类

确保已完成数据库表初始化后，从项目根目录运行：

```bash
python scripts/seed_categories.py
```

成功后会输出新增分类数和跳过分类数。脚本不会删除已有数据，也不会重复插入已存在分类。

默认分类包括社会保障、医疗卫生、教育服务、就业创业、住房保障、交通出行、市场监管、城市管理、公共安全、其他咨询。

### 2. 导入示例政策文档

项目在 `data/policies/` 下提供了少量模拟政策说明文档。运行：

```bash
python scripts/import_knowledge.py
```

脚本会把每个 `.md` 文件作为一条 `knowledge_docs` 记录导入数据库，标题来自文件名，来源为“本地示例政策文档”。同标题文档已存在时会自动跳过。

### 3. 知识库接口

启动后端后可访问以下接口：

```text
GET    /categories
POST   /categories
GET    /knowledge
GET    /knowledge/{id}
POST   /knowledge
PUT    /knowledge/{id}
DELETE /knowledge/{id}
GET    /knowledge/search?query=关键词
```

`GET /knowledge` 支持可选参数：

```text
category_id
status
keyword
```

默认只返回 `status=active` 的知识文档摘要，不返回过长正文。

### 4. 在 Swagger 中测试

启动后端：

```bash
cd backend
uvicorn app.main:app --reload
```

浏览器打开：

```text
http://localhost:8000/docs
```

可在 Swagger 中测试：

1. `POST /categories` 新增分类。
2. `GET /categories` 查看分类列表。
3. `POST /knowledge` 新增知识文档。
4. `GET /knowledge` 按分类、状态或关键词查询文档列表。
5. `GET /knowledge/{id}` 查看文档详情。
6. `PUT /knowledge/{id}` 修改文档内容。
7. `DELETE /knowledge/{id}` 将文档状态软删除为 `inactive`。
8. `GET /knowledge/search` 执行普通关键词搜索。

## 前端后续启动方式

当前前端提供 Vue 3 基础页面，可在问答页调用后端 `/chat` 接口。

```bash
cd frontend
npm install
npm run dev
```

启动后访问：

```text
http://127.0.0.1:5173/chat
```

可输入政务咨询问题，查看模板式回答、分类编号、问答时间和最近历史记录。

## 基础聊天问答

当前问答能力是“关键词检索 + 模板式回答”：

1. 后端接收用户问题。
2. 根据问题关键词判断政务分类。
3. 在 `knowledge_docs` 的 `title` 和 `content` 中进行普通 LIKE 检索。
4. 最多取 3 条相关政策文档。
5. 生成模板式回答。
6. 将问题、检索内容、回答、分类编号写入 `chat_records`。

当前不调用大模型 API，不使用 Chroma，不做文本向量化，也不是真正 RAG。

聊天接口会先检测用户输入中的手机号、身份证号、银行卡号、邮箱和可能的详细住址。检测到敏感信息时，系统会先脱敏，再将脱敏后的问题保存到 `chat_records`，并在回答中附加安全提示。

### 1. 启动后端

```bash
cd backend
uvicorn app.main:app --reload
```

### 2. 测试 `POST /chat`

可在 Swagger 中打开：

```text
http://localhost:8000/docs
```

请求示例：

```json
{
  "question": "城乡居民医保怎么参保？"
}
```

也可以用命令行测试：

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"城乡居民医保怎么参保？\"}"
```

### 3. 查看问答历史

```text
GET http://localhost:8000/chat/history
GET http://localhost:8000/chat/history?limit=10
GET http://localhost:8000/chat/{id}
```

## 敏感信息检测与脱敏

该功能属于政务数据安全基础能力，用于减少用户在咨询过程中提交完整个人敏感信息的风险。

### 1. 安全检测接口

Swagger 地址：

```text
http://localhost:8000/docs
```

接口：

```text
POST /safety/check
```

请求示例：

```json
{
  "text": "我的手机号是13812345678，身份证号是510101199901011234，邮箱是abc@example.com"
}
```

返回内容包含：

1. 原始输入 `original_text`。
2. 脱敏文本 `masked_text`。
3. 是否包含敏感信息 `has_sensitive_info`。
4. 敏感信息类型 `sensitive_types`。
5. 安全提示 `safety_warning`。

可在 Swagger 中分别测试手机号、身份证号、银行卡号、邮箱和较长详细地址文本。

### 2. `/chat` 自动脱敏

`POST /chat` 会自动执行敏感信息检测：

1. 如果问题包含敏感信息，后端会生成脱敏后的 `masked_question`。
2. 数据库 `chat_records.user_question` 保存脱敏后的问题。
3. 返回给前端的数据包含 `has_sensitive_info`、`sensitive_types`、`safety_warning` 和 `masked_question`。
4. 前端问答页会展示安全提醒，并提示系统实际保存的是脱敏后的问题。

## 用户反馈功能

当前已实现第七步用户反馈功能。用户在前端问答页收到回答后，可以对本次回答选择“有帮助”“没帮助”或“一般”，也可以填写可选文字反馈。反馈记录保存到 MySQL 的 `feedback` 表。

反馈评价只用于记录用户对当前模板式问答结果的主观评价，暂不接入大模型 API，不实现 RAG，不使用 Chroma。

### 1. 提交反馈

启动后端后，可在 Swagger 中测试：

```text
POST /feedback
```

请求示例：

```json
{
  "chat_id": 1,
  "rating": "helpful",
  "comment": "回答比较清楚"
}
```

`rating` 支持：

1. `helpful`：有帮助。
2. `unhelpful`：没帮助。
3. `neutral`：一般。

如果 `chat_id` 不存在，接口会返回清晰错误，提示无法提交反馈。

### 2. 查询反馈列表

```text
GET /feedback
GET /feedback?limit=20
```

`limit` 默认 50，最大 100，返回最近提交的反馈记录。

### 3. 查询反馈统计

```text
GET /feedback/statistics
```

返回示例：

```json
{
  "total": 3,
  "helpful_count": 1,
  "unhelpful_count": 1,
  "neutral_count": 1
}
```

### 4. 前端提交反馈

启动前端后访问：

```text
http://127.0.0.1:5173/chat
```

提交一个政务咨询问题并收到回答后，回答展示区域下方会出现反馈区。选择评价、填写可选文字反馈后点击“提交反馈”，成功后页面会提示：

```text
反馈已提交，感谢您的评价。
```

## 简单数据看板

当前已实现第八步简单数据看板。看板基于 MySQL 中已有的知识库文档、问答记录、用户反馈和政务分类数据做基础统计，不涉及大模型 API、RAG、Chroma 或方向二功能。

### 1. 看板接口

启动后端后，可在 Swagger 中测试：

```text
GET /dashboard
```

返回内容包括：

1. 知识库文档总数、有效政策文档数、问答总次数、用户反馈总数。
2. 有帮助、没帮助、一般三类反馈数量。
3. 各政务分类下的问答数量和知识文档数量。
4. 最近 5 条问答记录。
5. 最近 5 条反馈记录。

### 2. 前端数据看板页面

启动前端后访问：

```text
http://127.0.0.1:5173/dashboard
```

也可以从顶部导航栏点击“数据看板”进入。页面会展示顶部统计卡片、反馈统计、分类统计、最近问答和最近反馈。若数据为空，会显示无数据提示。

## 文本切分与 Chroma 向量索引

当前已实现第九步文本切分与本地 Chroma 向量数据库，为后续 RAG 检索增强问答做准备。本阶段只构建索引和测试检索接口，暂不改造 `/chat`，暂不接入 DeepSeek、通义千问或其他大模型 API。

### 1. 新增数据表

本阶段新增 `knowledge_chunks` 表，用于保存从 `knowledge_docs` active 文档切分出的文本片段。该表是派生数据，重新构建向量索引时会清空并重新生成，但不会删除 `knowledge_docs` 原始文档。

更新依赖后运行：

```bash
cd backend
pip install -r requirements.txt
```

从项目根目录创建新表：

```bash
python scripts/init_db.py
```

`create_all` 只会创建缺失表，不会删除已有表和已有数据。

### 2. 构建向量索引

从项目根目录运行：

```bash
python scripts/build_vector_index.py
```

脚本会读取 `status=active` 的知识文档，执行文本切分，写入 `knowledge_chunks`，并将对应文本片段写入本地 Chroma collection：

```text
gov_knowledge_chunks
```

Chroma 默认存储路径来自 `.env` 或默认配置：

```env
VECTOR_DB_PATH=./data/vector_db
```

`data/vector_db/` 下的 Chroma 数据文件不会提交到 Git，只保留 `.gitkeep` 占位。

### 3. 向量检索测试接口

启动后端后，可在 Swagger 中测试：

```text
GET /vector/status
GET /vector/search?query=医保报销需要哪些材料&limit=5
POST /vector/rebuild
```

`GET /vector/status` 返回 MySQL chunk 数量、Chroma 向量数量、collection 名称和向量数据库路径。

`GET /vector/search` 返回最相似的文本片段，包括文档编号、标题、切片序号、内容、distance 和 metadata。

`POST /vector/rebuild` 用于开发阶段手动重建索引。

### 4. 当前 embedding 说明

当前 embedding 使用轻量本地 hash 向量方案，固定 384 维，不调用外部 API，不下载模型，也不依赖 `sentence-transformers`、`torch`、`tensorflow` 等重型库。该方案仅用于本地演示和打通 RAG 流程，后续可替换为真实 embedding 模型或 embedding API。

## 基础 RAG 问答闭环

当前已实现第十步：`/chat` 已接入向量检索，形成“向量检索 + 模板式回答”的基础 RAG 问答闭环。该回答仍不是大模型生成，不调用 DeepSeek、通义千问或其他大模型 API。

### 1. 使用前准备

从项目根目录依次运行：

```bash
python scripts/init_db.py
python scripts/build_vector_index.py
```

如果尚未构建向量索引，`/chat` 会自动 fallback 到原有关键词检索逻辑，保证问答功能仍可使用。

### 2. `/chat` 检索逻辑

`POST /chat` 当前流程：

1. 先检测用户输入中的敏感信息。
2. 如包含手机号、身份证号、银行卡号等敏感信息，先生成脱敏问题。
3. 优先调用本地 Chroma 向量检索，检索相关政策片段。
4. 向量检索无结果或向量库未构建时，fallback 到原有 MySQL LIKE 关键词检索。
5. 如果两种方式都没有找到依据，返回知识库暂无直接依据的提示。
6. 将脱敏后的问题、检索内容、模板式回答和分类编号保存到 `chat_records`。

### 3. 新增返回字段

`/chat` 返回中新增：

1. `retrieval_mode`：`vector`、`keyword` 或 `none`。
2. `references`：参考依据列表，包含文档编号、标题、切片序号、片段内容、来源、分类编号和 distance。
3. `reference_count`：参考依据数量。

前端问答页会展示检索方式和“参考依据”区域。

### 4. 测试问题示例

可以在前端问答页或 Swagger 中测试：

```text
医保报销需要哪些材料
创业补贴怎么申请
居住证办理需要什么材料
公积金提取流程是什么
```

正式大模型 API 接入放在下一阶段之后，本阶段只完成 RAG 检索链路。

## 大模型 API 接入预留

当前已实现第十一步：系统预留大模型 API 接入能力，但默认关闭，不配置真实模型，也不要求 API Key。`/chat` 会尝试走大模型占位服务；当 `LLM_ENABLE=false` 或模型配置不完整时，会自动使用现有“向量检索 + 模板式 RAG 回答”。

### 1. 默认配置

`.env.example` 中提供以下占位项：

```env
LLM_ENABLE=false
LLM_PROVIDER=
LLM_API_KEY=
LLM_BASE_URL=
LLM_MODEL=
LLM_TIMEOUT=30
```

不要把真实 API Key 写入代码，也不要提交 `.env`。

### 2. 配置状态接口

启动后端后可测试：

```text
GET /llm/status
```

返回内容包含：

1. `enabled`：是否开启 LLM。
2. `available`：配置是否完整可用。
3. `provider` 和 `model`：当前配置的服务商和模型名。
4. `base_url_configured`：是否配置了服务地址。
5. `api_key_configured`：是否配置了 API Key，只返回布尔值，不返回密钥内容。

### 3. 后续启用方式

确定 DeepSeek、通义千问或其他 OpenAI-compatible API 后，在本地 `.env` 中修改：

```env
LLM_ENABLE=true
LLM_PROVIDER=具体模型服务
LLM_API_KEY=真实 API Key
LLM_BASE_URL=服务地址
LLM_MODEL=模型名称
```

当前代码中只保留 prompt 构建和调用占位，尚未发起任何外部 API 请求。

## 前端政务风格与知识库管理页面

当前已实现第十二步：前端整体风格统一为简洁正式的政务办公风格，并新增知识库管理页面。页面不引入 Element Plus、Ant Design 等大型 UI 框架，继续使用 Vue 原生组件和项目现有样式。

### 1. 前端导航

顶部导航包含：

1. 首页
2. 智能问答
3. 知识库管理
4. 数据看板

当前页面会有高亮状态。

### 2. 知识库管理功能

访问：

```text
http://127.0.0.1:5173/knowledge
```

支持：

1. 按关键词、分类、状态查询知识文档。
2. 新增知识文档。
3. 编辑标题、分类、来源、正文和状态。
4. 查看完整文档详情。
5. 调用 `DELETE /knowledge/{id}` 进行软删除，后端会将状态改为 `inactive`。
6. 页面显示 loading、错误提示、空数据提示和操作成功提示。

### 3. 首页优化

首页展示系统名称、项目简介和主要功能卡片，包括政策智能问答、政务知识库管理、敏感信息脱敏、数据统计看板、RAG 检索增强和大模型接口预留，并提供进入智能问答和知识库管理的入口。

当前仍未启用真实大模型 API，后续启用仍通过 `.env` 配置。

## 项目自检脚本

当前已新增项目一键检查脚本，用于最终验收、截图和提交前自检。脚本只检查现有接口可用性，不修改业务数据，不修改数据库结构，也不会接入真实大模型 API。

### 1. 启动后端服务

先在一个终端中启动后端：

```bash
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload
```

后端默认地址：

```text
http://127.0.0.1:8000
```

### 2. 运行项目自检

回到项目根目录运行：

```bash
python scripts/check_project.py
```

脚本默认检查 `http://127.0.0.1:8000`，会依次检查：

1. `GET /health`
2. `GET /database/ping`
3. `GET /categories`
4. `GET /knowledge`
5. `GET /vector/status`
6. `GET /llm/status`
7. `GET /dashboard`
8. `POST /chat`

如果需要检查其他后端地址，可使用：

```bash
python scripts/check_project.py --base-url http://127.0.0.1:8000
```

### 3. 常见提示处理

如果提示知识库为空，可运行：

```bash
python scripts/import_knowledge.py
```

也可以通过前端知识库管理页面新增政策文档。

如果提示向量索引为空，可运行：

```bash
python scripts/build_vector_index.py
```

当前大模型 API 为预留状态，`LLM_ENABLE=false` 时 `/llm/status` 显示 `available=false` 是正常情况，不需要填写真实 API Key。

## 当前阶段已完成内容

1. 创建后端 FastAPI 最小可运行结构。
2. 创建 `GET /health` 健康检查接口。
3. 创建前端 Vue 3 最小页面结构。
4. 创建首页和静态问答占位页。
5. 创建 `data` 数据目录占位。
6. 创建后续数据库初始化、知识导入、向量索引构建脚本占位。
7. 创建 `.env.example`、`.gitignore` 和基础 `docker-compose.yml`。
8. 创建 SQLAlchemy 数据库连接配置和核心数据表模型。
9. 创建数据库初始化脚本和数据库验证接口。
10. 创建政务分类和知识文档基础管理接口。
11. 创建默认政务分类初始化脚本。
12. 创建示例政策文档和普通数据库导入脚本。
13. 创建基础聊天问答接口和历史查询接口。
14. 前端问答页已接入后端 `/chat` 和 `/chat/history`。
15. 创建敏感信息检测接口，并在 `/chat` 中自动脱敏用户问题。
16. 创建用户反馈接口、反馈统计接口，并在前端问答页支持当前回答反馈提交。
17. 创建数据看板接口，并在前端新增数据看板页面。
18. 创建 `knowledge_chunks` 表模型、文本切分服务、本地 hash embedding 服务、Chroma 向量索引构建脚本和向量检索测试接口。
19. 将向量检索接入 `/chat`，形成基础 RAG 问答闭环，并在前端展示检索方式和参考依据。
20. 预留大模型 API 配置、LLM 服务占位和 `/llm/status` 状态接口，默认关闭并 fallback 到模板式 RAG。
21. 优化前端政务风格，新增知识库管理页面，支持知识文档查询、新增、编辑、查看和软删除。

## 下一阶段计划

下一阶段建议进入“真实大模型 API 调用实现或前端知识库管理页面”：

1. 确定 DeepSeek、通义千问或其他模型服务后，实现 `llm_service.generate_answer_with_llm` 的真实 API 调用。
2. 可以继续增强知识库管理，例如新增向量索引重建入口或按分类批量筛选。
3. 后续再评估是否替换真实 embedding 模型或 embedding API。
4. 继续避免过早接入大模型调用和复杂前端功能。
