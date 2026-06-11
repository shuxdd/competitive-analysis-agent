# 知识库模块

知识库模块提供向量数据库管理和语义检索功能，用于存储和检索竞品信息。

## 模块结构

```
knowledge/
├── __init__.py          # 模块导出
├── vector_store.py      # 向量数据库管理
├── embeddings.py        # Embedding服务
├── knowledge_base.py    # 知识库管理
└── README.md            # 本文件
```

## 核心功能

### 1. 向量数据库管理 (VectorStore)

基于Chroma的向量数据库，提供：
- 集合管理（创建、删除、清空）
- 文档管理（添加、更新、删除）
- 语义检索（支持元数据过滤）

### 2. Embedding服务

支持两种Embedding方式：
- **OpenAI Embedding**: 使用`text-embedding-3-small`模型
- **本地Embedding**: 使用`sentence-transformers`库

### 3. 知识库管理 (KnowledgeBase)

整合向量数据库和Embedding服务，提供：
- 竞品信息管理
- 网页内容存储
- 用户评价管理
- 语义检索
- 上下文获取（用于RAG）

## 使用示例

### 基本使用

```python
from knowledge import KnowledgeBase

# 创建知识库实例
kb = KnowledgeBase(
    persist_dir="./data/chroma",
    embedding_type="openai"
)

# 添加竞品信息
competitor_data = {
    "company_info": {
        "company_name": "示例公司",
        "founded": "2020"
    },
    "products": [
        {
            "name": "产品1",
            "description": "产品描述",
            "features": ["功能1", "功能2"]
        }
    ],
    "target_market": "目标市场",
    "key_differentiators": ["差异化1"]
}

kb.add_competitor("comp_001", competitor_data)

# 搜索竞品信息
results = kb.search_competitors(
    query="产品功能",
    competitor_id="comp_001"
)

# 获取竞品上下文（用于RAG）
context = kb.get_competitor_context(
    competitor_id="comp_001",
    query="公司背景",
    max_tokens=3000
)
```

### 使用本地Embedding

```python
from knowledge import KnowledgeBase

# 使用本地Embedding模型
kb = KnowledgeBase(
    persist_dir="./data/chroma",
    embedding_type="local",
    model_name="all-MiniLM-L6-v2",
    device="cpu"
)
```

### 管理用户评价

```python
# 添加用户评价
kb.add_user_review(
    competitor_id="comp_001",
    review_content="这个产品很好用",
    rating=4.5,
    source="app_store"
)

# 搜索用户评价
results = kb.search_reviews(
    query="好用",
    competitor_id="comp_001",
    min_rating=4.0
)
```

## 数据结构

### 竞品信息

```python
{
    "company_info": {
        "company_name": "公司名称",
        "founded": "成立时间",
        "location": "所在地",
        "funding": "融资情况",
        "employees": "员工规模"
    },
    "products": [
        {
            "name": "产品名称",
            "description": "产品描述",
            "features": ["功能1", "功能2"],
            "pricing": {
                "model": "定价模式",
                "tiers": [...]
            }
        }
    ],
    "target_market": "目标市场",
    "key_differentiators": ["差异化1", "差异化2"]
}
```

### 检索结果

```python
{
    "id": "文档ID",
    "document": "文档内容",
    "metadata": {
        "competitor_id": "竞品ID",
        "type": "内容类型",
        "source": "数据来源"
    },
    "distance": 0.1,  # 距离（越小越相似）
    "similarity": 0.9  # 相似度（越大越相似）
}
```

## 配置说明

### 向量数据库配置

- `persist_dir`: 持久化目录，默认`./data/chroma`
- `anonymized_telemetry`: 是否启用匿名遥测，默认`False`

### Embedding配置

- `model`: 模型名称，默认`text-embedding-3-small`
- `api_key`: API密钥（从环境变量读取）
- `api_base`: API基础URL（从环境变量读取）

## 依赖项

- `chromadb`: 向量数据库
- `langchain-openai`: OpenAI Embedding
- `sentence-transformers`: 本地Embedding（可选）

## 运行测试

```bash
# 运行简单测试（使用mock）
python -m pytest tests/test_knowledge_simple.py -v

# 运行完整测试（需要真实数据库）
python -m pytest tests/test_knowledge.py -v
```

## 注意事项

1. **首次运行**: Chroma数据库会在指定目录创建文件
2. **内存使用**: 大量文档可能占用较多内存
3. **Embedding成本**: 使用OpenAI Embedding会产生API费用
4. **本地模型**: 使用本地Embedding需要下载模型文件
