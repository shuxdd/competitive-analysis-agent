# 数据源扩展方案：GitHub + 应用商店

## 目标

新增 2 个数据源采集器，丰富竞品分析的数据维度。

## 数据源 1：GitHub 采集器

### 采集内容

| 字段 | 说明 |
|------|------|
| repo 基本信息 | star/fork/watcher 数量、描述、语言、License |
| 活跃度 | 最近 commit 时间、近 30 天 commit 数、issue 响应时间 |
| 贡献者 | 贡献者数量、top 10 贡献者 |
| Release | 最新版本号、发布时间、更新频率 |

### 技术方案

- **库**: `PyGithub` 或直接调 GitHub REST API v3
- **认证**: 支持可选的 `GITHUB_TOKEN`（无 token 限 60 次/小时，有 token 5000 次/小时）
- **缓存**: 复用现有 `CacheManager`，缓存 24 小时

### 接口设计

```python
class GitHubCollector(BaseCollector):
    async def collect(self, target: str, **kwargs) -> Dict:
        """target = owner/repo 或竞品名称自动搜索"""

    def parse(self, raw_data) -> Dict:
        """提取 star/fork/commit/release 等结构化数据"""

    async def search_repo(self, keyword: str) -> List[Dict]:
        """按关键词搜索仓库"""

    async def get_repo_stats(self, owner: str, repo: str) -> Dict:
        """获取仓库详细统计"""
```

### 输出示例

```json
{
  "repo": "notionhq/notion-sdk-js",
  "stars": 12500,
  "forks": 800,
  "open_issues": 45,
  "language": "TypeScript",
  "license": "MIT",
  "last_commit": "2026-06-10",
  "commits_30d": 23,
  "contributors_count": 156,
  "latest_release": "v2.3.0",
  "release_date": "2026-05-20"
}
```

---

## 数据源 2：应用商店采集器

### 采集内容

| 字段 | 说明 |
|------|------|
| App 基本信息 | 名称、开发者、分类、图标、描述 |
| 评分 | 平均评分、评分数量 |
| 评论 | 最近 N 条评论（文本 + 评分 + 时间） |
| 版本 | 当前版本号、更新时间、版本历史 |

### 数据源优先级

| 平台 | 方案 | 说明 |
|------|------|------|
| Google Play | `google-play-scraper` 库 | 免费、稳定、支持中文 |
| App Store | `app-store-scraper` 库 | 免费、支持中文 |
| 国内安卓（华为/小米） | 暂不支持，后续扩展 | 反爬较严，优先级低 |

### 接口设计

```python
class AppStoreCollector(BaseCollector):
    async def collect(self, target: str, **kwargs) -> Dict:
        """target = app名称 或 app_id"""

    def parse(self, raw_data) -> Dict:
        """提取评分/评论/版本等结构化数据"""

    async def search_app(self, keyword: str, store: str = "google") -> List[Dict]:
        """搜索应用"""

    async def get_reviews(self, app_id: str, store: str = "google", count: int = 20) -> List[Dict]:
        """获取评论"""

    async def get_app_info(self, app_id: str, store: str = "google") -> Dict:
        """获取应用详情"""
```

### 输出示例

```json
{
  "app_name": "Notion",
  "store": "google_play",
  "rating": 4.6,
  "ratings_count": 152000,
  "installs": "10,000,000+",
  "current_version": "0.6.40",
  "last_updated": "2026-06-01",
  "reviews": [
    {
      "text": "功能强大但偶尔卡顿",
      "rating": 4,
      "date": "2026-06-10",
      "user": "张三"
    }
  ]
}
```

---

## 集成方式

### Agent 流程对接

在现有 LangGraph 流程的「数据采集」节点中，根据竞品类型自动选择数据源：

```
planner → searcher → [GitHub? → GitHubCollector] → [App? → AppStoreCollector] → scraper → extractor → analyzer → reporter
```

规划器根据竞品标签决定是否调用：
- 标签含 `开源`/`开发者工具`/`GitHub` → 调 GitHub
- 标签含 `App`/`移动`/`C端` → 调应用商店
- 两者可同时调用

### 文件结构

```
collector/
  __init__.py          # 新增导出
  base.py              # 不变
  web_search.py        # 不变
  web_scraper.py       # 不变
  cleaner.py           # 不变
  github_collector.py  # 新增
  app_store_collector.py  # 新增
```

### 依赖新增

```
# requirements.txt 新增
PyGithub>=2.1.0
google-play-scraper>=1.2.0
app-store-scraper>=0.3.5
```

---

## 工作量估算

| 任务 | 工作量 |
|------|--------|
| GitHubCollector 实现 + 测试 | 2h |
| AppStoreCollector 实现 + 测试 | 2h |
| Agent 流程集成 | 1h |
| 文档更新 | 0.5h |
| **合计** | **5.5h** |
