# 前端模块

智能竞品分析 Agent 的前端界面，基于 React + TypeScript 构建。

## 技术栈

- **构建工具**: Vite 8
- **框架**: React 18 + TypeScript 5
- **样式**: Tailwind CSS 4
- **UI 组件**: shadcn/ui (按需复制)
- **路由**: React Router 6
- **状态管理**: TanStack Query (React Query) v5
- **HTTP 客户端**: Axios
- **图表**: Recharts
- **图标**: lucide-react
- **Markdown**: react-markdown + remark-gfm
- **通知**: sonner

## 启动命令

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

开发服务器默认运行在 http://localhost:5173

## 目录结构

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn/ui 组件
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── input.tsx
│   │   │   ├── table.tsx
│   │   │   └── ...
│   │   └── layout/          # 布局组件
│   │       ├── Sidebar.tsx
│   │       └── Topbar.tsx
│   ├── pages/               # 页面组件
│   │   ├── dashboard/       # 仪表盘
│   │   ├── competitors/     # 竞品管理
│   │   ├── analysis/        # 分析任务
│   │   ├── reports/         # 报告中心
│   │   └── qa/              # 智能问答
│   ├── layouts/             # 布局
│   │   └── MainLayout.tsx
│   ├── lib/                 # 工具库
│   │   ├── api.ts           # axios 封装
│   │   ├── queryClient.ts   # React Query 配置
│   │   └── utils.ts         # 工具函数
│   ├── hooks/               # 自定义 hooks
│   │   └── useTheme.ts      # 主题切换
│   ├── types/               # TypeScript 类型
│   │   └── index.ts
│   ├── styles/              # 样式
│   │   └── globals.css
│   ├── App.tsx              # 应用入口
│   └── main.tsx             # 渲染入口
├── public/                  # 静态资源
├── index.html               # HTML 模板
├── package.json
├── tsconfig.json
├── vite.config.ts
└── postcss.config.js
```

## 已实现功能

### 1. 仪表盘 (`/`)
- 数据概览卡片（竞品总数、监控中、分析任务数、报告数）
- 最近任务列表
- 最近报告列表

### 2. 竞品管理 (`/competitors`)
- 竞品列表（分页、搜索）
- 新建竞品（Dialog 表单）
- 编辑竞品
- 删除竞品

### 3. 分析任务 (`/analysis`)
- 任务列表（状态展示）
- 新建分析（多选竞品、选择维度）
- 任务状态展示（pending/running/completed/failed）

### 4. 报告中心 (`/reports`)
- 报告卡片网格视图
- 搜索功能
- 报告详情（待完善）

### 5. 智能问答 (`/qa`)
- ChatGPT 风格对话界面
- 消息发送（Enter 发送，Shift+Enter 换行）
- 打字机效果（模拟流式输出）
- 消息复制、点赞/点踩

## 环境变量

创建 `.env` 文件（可选）：

```env
VITE_API_URL=http://localhost:8000
```

默认连接 http://localhost:8000

## 后端依赖

前端需要后端 API 服务运行在 http://localhost:8000

```bash
# 在项目根目录启动后端
cd ..
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

## 主题切换

支持亮色/暗色模式切换，状态持久化到 localStorage。

## 开发规范

- 使用 `@/` 路径别名导入模块
- 组件使用 shadcn/ui 风格
- 样式使用 Tailwind CSS 类名
- 数据请求使用 React Query
- 类型定义在 `src/types/index.ts`
