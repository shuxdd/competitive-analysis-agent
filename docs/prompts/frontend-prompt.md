# 任务：为竞品分析 Agent 项目生成前端界面

## 项目背景

这是一个基于 LLM 的智能竞品分析系统，后端已用 FastAPI 完整实现（91 个测试用例全部通过）。
- 后端代码目录：`api/`（FastAPI 路由：competitors、analysis、reports、qa）
- 数据模型：`models/`
- Agent 核心：`agent/`（基于 LangGraph 状态图）
- 启动方式：`uvicorn api.app:app --reload --host 0.0.0.0 --port 8000`
- API 文档：`http://localhost:8000/docs`

你需要在前端没有代码的情况下，从零开始搭建一个完整的前端工程 `frontend/`。

## 完整项目目录结构（必须先熟悉）

```
competitive-analysis-agent/
├── agent/                  # Agent 核心（LangGraph 状态图、节点、工具）
│   ├── nodes/              # 节点：planner、searcher、scraper、extractor、analyzer、reporter
│   ├── tools/              # 工具：scraper_tool、search_tool、vector_tool
│   ├── graph.py            # LangGraph 状态图定义
│   ├── graph_state.py      # 状态类型
│   └── llm.py              # LLM 客户端封装
├── api/                    # FastAPI 接口层
│   ├── routers/            # 路由：competitors、analysis、reports、qa
│   ├── app.py              # FastAPI 入口（含 CORS 配置）
│   ├── database.py         # SQLAlchemy ORM + 依赖注入
│   └── schemas.py          # Pydantic 请求/响应模型
├── collector/              # 数据采集（搜索、爬取、清洗）
│   ├── base.py
│   ├── web_scraper.py      # Selenium + BeautifulSoup
│   ├── web_search.py       # SerpAPI
│   └── cleaner.py
├── config/                 # 配置管理
│   ├── settings.py         # 环境变量 + 配置项
│   └── prompts.py          # Prompt 模板
├── knowledge/              # 知识库（向量存储、Embedding、RAG）
│   ├── embeddings.py
│   ├── vector_store.py     # Chroma
│   └── knowledge_base.py
├── models/                 # 数据模型（Pydantic）
│   ├── competitor.py
│   ├── analysis.py
│   └── report.py
├── report/                 # 报告生成
│   ├── generator.py
│   ├── templates.py
│   └── templates/          # 报告模板
├── display/                # 展示层（占位）
├── utils/                  # 工具类（占位）
├── examples/               # 独立可运行的 demo
├── tests/                  # 单元测试（91 个用例全通过）
├── docs/                   # 文档与方案
├── frontend/               # ⚠️ 你要在本目录下创建
├── CLAUDE.md               # 项目规范（必读）
├── DEVELOPMENT_PROGRESS.md # 开发进度
├── PRD.md                  # 产品需求
├── TECHNICAL_ARCHITECTURE.md
├── requirements.txt
├── pyproject.toml
└── README.md
```

**关键提示**：
- 所有 Python 模块的 import 都遵循 `from xxx import yyy` 风格，避免循环依赖
- 后端日志统一用 `logging.getLogger(__name__)`
- 所有时间字段用 `datetime` ISO 格式字符串
- 前端类型定义要严格对齐 `api/schemas.py` 的字段

## 技术栈（必须严格遵守，与 CLAUDE.md 一致）

- **构建工具**：Vite 5+
- **框架**：React 18+ + TypeScript 5+
- **样式**：Tailwind CSS 3+（不要用 CSS-in-JS 或其他方案）
- **UI 组件库**：shadcn/ui（按需复制组件到 `src/components/ui/`，不要安装整个包）
- **路由**：React Router 6
- **状态/数据请求**：TanStack Query (React Query) v5
- **HTTP**：Axios
- **图表**：Recharts（轻量、TypeScript 友好）
- **图标**：lucide-react
- **Markdown 渲染**：react-markdown + remark-gfm
- **代码规范**：ESLint + Prettier
- **包管理**：npm 或 pnpm 都行，但要在 README 中说明

## 后端 API 对接规范

后端统一响应格式（FastAPI 已实现）：
- 通用响应：`{ code: 200, data: any, message: string }`
- 分页响应：`{ code: 200, data: any[], total: number, page: number, page_size: number, message: string }`
- 错误响应：`{ code: 非200, data: null, message: 错误信息 }`

主要接口（具体以 `http://localhost:8000/docs` 为准）：
- `GET /api/competitors?page=1&page_size=20&keyword=&industry=` - 竞品列表（分页）
- `POST /api/competitors` - 创建竞品
- `GET /api/competitors/{id}` - 竞品详情
- `PUT /api/competitors/{id}` - 更新竞品
- `DELETE /api/competitors/{id}` - 删除竞品
- `POST /api/analysis` - 提交分析任务（body: `{ competitors: string[], analysis_type, dimensions, my_product }`）
- `GET /api/analysis/{task_id}` - 查询分析任务状态
- `GET /api/reports` - 报告列表
- `GET /api/reports/{id}` - 报告详情
- `POST /api/qa` - 智能问答（body: `{ question, context? }`）

请求封装要求：在 `src/lib/api.ts` 中创建 axios 实例，配置：
- baseURL: `http://localhost:8000`
- 拦截器统一处理 `{code, data, message}`，code !== 200 时抛出错误
- 拦截器在请求时把后端返回的 `data` 字段解包出来，业务代码只关心业务数据

## 需要实现的功能页面

### 1. 全局布局（`src/layouts/MainLayout.tsx`）
- 左侧固定侧边栏（Logo + 导航菜单 + 用户信息）
- 顶部 Topbar（面包屑、搜索、通知、用户头像）
- 主内容区（基于 React Router 的 `<Outlet />`）
- 响应式：移动端侧边栏可折叠

### 2. Dashboard 首页（`/`）
- 数据概览卡片：竞品总数、监控中、分析任务数、报告数
- 最近动态时间线：展示最近的分析任务和报告
- 趋势图表：近 7/30 天分析任务数量（Recharts 折线图）
- 行业分布：竞品按行业分类的饼图

### 3. 竞品管理
- **列表页**（`/competitors`）：
  - 表格 + 搜索框 + 行业筛选 + 新建按钮
  - 支持分页、行操作（查看/编辑/删除/分析）
  - 批量操作：批量删除
- **详情页**（`/competitors/:id`）：
  - 基本信息卡片（公司名、官网、行业、标签、备注）
  - Tab 切换：基本信息 / 历史报告 / 分析历史 / 相关动态
  - 右侧浮动按钮："立即分析"
- **新建/编辑**：用 Dialog 表单，字段：name、website、industry、tags（多选）、notes

### 4. 分析任务（`/analysis`）
- **任务列表**：表格展示任务状态（pending/running/completed/failed）+ 进度条
- **新建分析**：表单（多选竞品、选择分析维度 features/pricing/swot/marketing、输入我方产品名）
- **任务详情页**（`/analysis/:task_id`）：
  - 任务状态实时刷新（用 React Query 的 refetchInterval，3 秒一次）
  - Agent 执行过程可视化：用步骤条/时间线展示 LangGraph 节点流转（scraper → searcher → extractor → analyzer → reporter）
  - 完成后展示结果摘要 + "查看完整报告"按钮

### 5. 报告中心（`/reports`）
- **列表页**：卡片网格视图，每张卡显示报告标题、关联竞品、生成时间、摘要
- **详情页**（`/reports/:id`）：
  - 左侧报告目录（自动从 Markdown 标题生成）
  - 主区域渲染 Markdown（包含标题、段落、列表、表格、代码块、引用）
  - 嵌入的图表用 Recharts 渲染（如果报告 JSON 里有图表数据）
  - 顶部操作栏：导出 PDF（可选，本期可只做按钮占位）、复制 Markdown

### 6. 智能问答（`/qa`）
- 类 ChatGPT 对话界面
- 左侧历史对话列表
- 主区域：消息流（用户右对齐、AI 左对齐，AI 消息用 Markdown 渲染）
- 输入框固定底部，支持 Enter 发送、Shift+Enter 换行
- AI 回复时显示"思考中"动画 + 打字机效果（逐字输出，调用流式接口；如后端无流式接口则用 setInterval 模拟）
- 消息可点赞/点踩

## 视觉设计规范

参考 Linear、Notion AI、Perplexity 的现代 AI 工具风格：

### 颜色（通过 Tailwind 配置 + CSS 变量）
- 主色：`indigo-600` (#4F46E5) 用于主按钮、链接、强调
- 强调色：`violet-500` 用于 AI 相关元素
- 背景：`slate-50` (浅) / `slate-950` (暗色模式)
- 卡片：`white` / `slate-900`，带 `shadow-sm` 边框
- 文字：分层灰度（`slate-900` / `slate-600` / `slate-400`）

### 设计原则
- **克制的留白**：卡片 padding 至少 24px
- **圆角统一**：组件 `rounded-lg` (8px)，按钮 `rounded-md` (6px)
- **阴影轻量化**：默认 `shadow-sm`，hover 时 `shadow-md`
- **微动效**：hover/active 状态有过渡动画（`transition-all duration-200`）
- **暗色模式**：必须支持，通过顶部按钮切换，状态持久化到 localStorage

### 字体
- 中文：PingFang SC / Microsoft YaHei
- 英文/数字：Inter
- 等宽：JetBrains Mono（代码块）

## 目录结构

```
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn/ui 组件（按需添加）
│   │   ├── layout/          # 布局相关
│   │   ├── charts/          # 图表封装
│   │   └── common/          # 通用业务组件
│   ├── pages/               # 页面（按功能模块分子目录）
│   │   ├── dashboard/
│   │   ├── competitors/
│   │   ├── analysis/
│   │   ├── reports/
│   │   └── qa/
│   ├── layouts/             # 布局
│   ├── lib/
│   │   ├── api.ts           # axios 实例 + 拦截器
│   │   ├── queryClient.ts   # React Query 配置
│   │   └── utils.ts         # shadcn 工具函数 (cn)
│   ├── hooks/               # 自定义 hooks
│   ├── types/               # TypeScript 类型定义（与后端 schema 对应）
│   ├── styles/
│   │   └── globals.css      # Tailwind 入口 + CSS 变量（暗色模式）
│   ├── App.tsx
│   └── main.tsx
├── .env.example             # VITE_API_BASE_URL=http://localhost:8000
├── .gitignore
├── index.html
├── package.json
├── tailwind.config.js
├── postcss.config.js
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## 开发流程（按 CLAUDE.md 规范执行）

1. **初始化项目**
   - `npm create vite@latest frontend -- --template react-ts`
   - 安装并配置 Tailwind CSS（参考官方 v3 流程）
   - 配置 shadcn/ui（`npx shadcn-ui@latest init`）
   - 配置 path alias `@/` 指向 `src/`
   - 配置 ESLint + Prettier

2. **搭建基础设施**
   - axios 实例 + 拦截器
   - React Query Provider
   - Router 配置（含路由懒加载）
   - 全局 Layout
   - 主题切换（亮/暗）

3. **分模块开发**（每完成一个模块独立 commit）
   - 模块 1：Dashboard + 通用组件
   - 模块 2：竞品管理（CRUD）
   - 模块 3：分析任务（含状态轮询）
   - 模块 4：报告中心（含 Markdown 渲染）
   - 模块 5：智能问答（含流式输出模拟）

4. **代码 Review（自检）**
   - TypeScript 严格模式开启，无 `any` 滥用
   - 所有异步操作正确处理 loading / error 状态
   - 表单有校验（用 react-hook-form + zod）
   - 列表有 loading skeleton 和 empty state
   - 错误用 toast 提示（sonner）

5. **文档同步更新**
   - 完成后更新根目录的 `CLAUDE.md`：把 frontend 状态从 ⏳ 改为 ✅
   - 在 `DEVELOPMENT_PROGRESS.md` 中追加本次进展
   - 在 `frontend/README.md` 中说明：技术栈、启动命令、目录结构、已实现功能

## 验收标准

- [ ] `cd frontend && npm install && npm run dev` 能成功启动，访问 `http://localhost:5173` 不报错
- [ ] 能完整跑通：登录态可选 → Dashboard 看数据 → 创建竞品 → 提交分析任务 → 看到任务执行过程 → 查看生成的报告 → 智能问答
- [ ] 后端 API 全部对接（参考 `/docs`），接口错误能友好提示
- [ ] 亮/暗模式切换正常，刷新后保持
- [ ] 响应式：在 1280px 和 768px 两个断点下都不变形
- [ ] TypeScript 编译无错误，ESLint 无 error
- [ ] `frontend/README.md` 完整，启动命令、目录结构、已实现页面都列清楚

## 注意事项

- **不要修改后端代码**，只在 `frontend/` 目录工作
- 不要做花里胡哨的动画，克制专业为主
- 所有用户可见的中文要简洁，不要用机翻腔
- 不确定的后端字段先在 `http://localhost:8000/docs` 查 Swagger，不要瞎猜
- 如果后端有 CORS 跨域问题（看 `api/app.py` 已配置 `allow_origins=["*"]`），前端不用处理
- 完成所有功能后，最后再写一份 `frontend/README.md` 给接手的人看
