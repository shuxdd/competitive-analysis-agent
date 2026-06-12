# Utils 模块设计文档

## 1. 概述

### 1.1 目标

设计并实现 `utils/` 工具模块，提取项目中的通用功能，消除代码重复，提高代码可维护性和复用性。

### 1.2 范围

包含 10 个通用功能：
1. LLM JSON 解析
2. 报告头部生成
3. 报告数据序列化
4. 降级报告生成
5. 文本清洗
6. ChromaDB 元数据清洗
7. 文本分块
8. 日期格式化
9. JSON 序列化
10. 统一日志配置

### 1.3 设计原则

- **单一职责**：每个文件专注于一个功能领域
- **纯函数优先**：尽可能使用纯函数，便于测试和复用
- **类型安全**：完整的类型注解
- **向后兼容**：重构时保持函数签名兼容

## 2. 架构设计

### 2.1 文件结构

```
utils/
├── __init__.py              # 模块导出
├── llm_parser.py           # LLM JSON 解析
├── report_helpers.py       # 报告相关工具
├── text_utils.py           # 文本清洗、分块
├── metadata_utils.py       # ChromaDB 元数据清洗
├── date_utils.py           # 日期格式化
├── json_utils.py           # JSON 序列化
├── logger.py               # 统一日志配置
└── tests/
    ├── __init__.py
    ├── test_llm_parser.py
    ├── test_report_helpers.py
    ├── test_text_utils.py
    ├── test_metadata_utils.py
    ├── test_date_utils.py
    ├── test_json_utils.py
    └── test_logger.py
```

### 2.2 依赖关系

```
logger.py (无依赖)
├── date_utils.py (无依赖)
├── json_utils.py (无依赖)
├── text_utils.py (无依赖)
├── metadata_utils.py (无依赖)
├── llm_parser.py (无依赖)
└── report_helpers.py (依赖 date_utils, json_utils)
```

## 3. 功能详细设计

### 3.1 LLM JSON 解析 (llm_parser.py)

**功能**：从 LLM 响应中提取 JSON，处理 markdown 代码块包裹的情况。

**函数签名**：

```python
def extract_json_from_llm(response: str) -> dict | list | None:
    """
    从 LLM 响应中提取 JSON。

    处理情况：
    1. 纯 JSON 字符串
    2. markdown 代码块包裹的 JSON（```json ... ```）
    3. 包含其他文本的 JSON

    参数：
        response: LLM 响应文本

    返回：
        解析后的 dict/list，失败返回 None
    """
```

**使用位置**：
- `agent/nodes/planner.py`
- `agent/nodes/extractor.py`
- `agent/nodes/analyzer.py`

### 3.2 报告相关工具 (report_helpers.py)

**功能**：报告头部生成、数据序列化、降级报告生成。

**函数签名**：

```python
def generate_report_header(title: str, competitors: list[str], report_type: str) -> str:
    """
    生成报告头部。

    参数：
        title: 报告标题
        competitors: 竞品名称列表
        report_type: 报告类型（quick/standard/deep）

    返回：
        Markdown 格式的报告头部
    """

def prepare_analysis_data(analysis_result: dict) -> dict:
    """
    准备报告数据，将 AnalysisResult 转换为报告模板可用的格式。

    参数：
        analysis_result: 分析结果字典

    返回：
        报告模板可用的数据字典
    """

def generate_fallback_report(competitor_name: str, analysis_data: dict) -> str:
    """
    生成降级报告（当 LLM 失败时）。

    参数：
        competitor_name: 竞品名称
        analysis_data: 分析数据

    返回：
        简化的 Markdown 报告
    """
```

**使用位置**：
- `agent/nodes/reporter.py`
- `report/generator.py`

### 3.3 文本工具 (text_utils.py)

**功能**：文本清洗、文本分块。

**函数签名**：

```python
def clean_text(text: str) -> str:
    """
    清洗文本：去除多余空白、特殊字符。

    参数：
        text: 原始文本

    返回：
        清洗后的文本
    """

def split_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    将文本分块。

    参数：
        text: 原始文本
        chunk_size: 块大小（字符数）
        overlap: 重叠字符数

    返回：
        文本块列表
    """
```

**使用位置**：
- `collector/cleaner.py`
- `collector/web_scraper.py`
- `knowledge/knowledge_base.py`

### 3.4 元数据工具 (metadata_utils.py)

**功能**：ChromaDB 元数据清洗。

**函数签名**：

```python
def sanitize_metadata(metadata: dict) -> dict:
    """
    清洗元数据，确保 ChromaDB 兼容。

    处理：
    1. list -> 逗号分隔字符串
    2. dict -> JSON 字符串
    3. None -> 空字符串
    4. 其他类型保持不变

    参数：
        metadata: 原始元数据字典

    返回：
        清洗后的元数据字典
    """
```

**使用位置**：
- `knowledge/vector_store.py`

### 3.5 日期工具 (date_utils.py)

**功能**：日期格式化。

**函数签名**：

```python
def format_datetime(dt: datetime = None, format_str: str = "%Y-%m-%d %H:%M") -> str:
    """
    格式化日期时间。

    参数：
        dt: datetime 对象，默认为当前时间
        format_str: 格式字符串

    返回：
        格式化后的日期字符串
    """

def get_current_timestamp() -> str:
    """
    获取当前时间戳（ISO 格式）。

    返回：
        ISO 格式的时间戳字符串
    """
```

**使用位置**：
- `agent/nodes/reporter.py`
- `report/generator.py`
- `api/` 各路由

### 3.6 JSON 工具 (json_utils.py)

**功能**：JSON 序列化。

**函数签名**：

```python
def json_serialize(obj: any, indent: int = 2) -> str:
    """
    JSON 序列化，处理中文和特殊类型。

    参数：
        obj: 要序列化的对象
        indent: 缩进空格数

    返回：
        JSON 字符串
    """

def json_dumps_pretty(obj: any) -> str:
    """
    美化 JSON 输出（ensure_ascii=False, indent=2, default=str）。

    参数：
        obj: 要序列化的对象

    返回：
        美化后的 JSON 字符串
    """
```

**使用位置**：
- `agent/nodes/*`
- `agent/tools/*`
- `report/generator.py`

### 3.7 日志工具 (logger.py)

**功能**：统一日志配置。

**函数签名**：

```python
def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    配置日志记录器。

    参数：
        name: 日志记录器名称
        level: 日志级别

    返回：
        配置好的日志记录器
    """

def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器（如果未配置则自动配置）。

    参数：
        name: 日志记录器名称

    返回：
        日志记录器
    """
```

**配置**：
- 日志格式：`%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- 输出：控制台 + 文件（`logs/app.log`）
- 日志轮转：按大小（10MB）或时间（每天）

**使用位置**：
- 全项目

## 4. 重构计划

### 4.1 重构顺序

**第一阶段：基础工具**
1. `logger.py` - 日志配置
2. `date_utils.py` - 日期格式化
3. `json_utils.py` - JSON 序列化
4. `text_utils.py` - 文本清洗、分块

**第二阶段：专用工具**
5. `llm_parser.py` - LLM JSON 解析
6. `metadata_utils.py` - ChromaDB 元数据清洗

**第三阶段：报告工具**
7. `report_helpers.py` - 报告相关工具

### 4.2 重构策略

- 每个阶段完成后运行测试确保不破坏功能
- 使用 `replace_all` 批量替换重复代码
- 保持函数签名兼容，避免破坏现有调用

### 4.3 重构范围

| 文件 | 重构内容 | 影响范围 |
|------|----------|----------|
| `agent/nodes/planner.py` | 替换 JSON 解析代码 | 低 |
| `agent/nodes/extractor.py` | 替换 JSON 解析代码 | 低 |
| `agent/nodes/analyzer.py` | 替换 JSON 解析代码 | 低 |
| `agent/nodes/reporter.py` | 替换报告生成代码 | 中 |
| `report/generator.py` | 替换报告生成代码 | 中 |
| `collector/cleaner.py` | 替换文本清洗代码 | 低 |
| `collector/web_scraper.py` | 替换文本清洗代码 | 低 |
| `knowledge/knowledge_base.py` | 替换文本分块代码 | 低 |
| `knowledge/vector_store.py` | 替换元数据清洗代码 | 低 |
| 全项目 | 替换日志配置 | 高 |

## 5. 测试策略

### 5.1 测试覆盖目标

90%+ 代码覆盖率

### 5.2 测试方法

- 每个函数至少 3 个测试用例（正常情况、边界情况、异常情况）
- 使用 `pytest` 和 `pytest-asyncio`
- Mock 外部依赖（文件系统、时间等）

### 5.3 测试文件结构

```
utils/tests/
├── __init__.py
├── test_llm_parser.py        # 5-8 个测试用例
├── test_report_helpers.py    # 8-10 个测试用例
├── test_text_utils.py        # 6-8 个测试用例
├── test_metadata_utils.py    # 4-6 个测试用例
├── test_date_utils.py        # 4-6 个测试用例
├── test_json_utils.py        # 4-6 个测试用例
└── test_logger.py            # 3-5 个测试用例
```

### 5.4 测试运行命令

```bash
pytest utils/tests/ -v --cov=utils --cov-report=html
```

## 6. 成功标准

### 6.1 功能标准

- 所有 10 个功能实现完成
- 所有函数有完整的类型注解
- 所有函数有中文文档字符串

### 6.2 质量标准

- 测试覆盖率 90%+
- 所有测试通过
- 无重复代码

### 6.3 重构标准

- 现有代码中的重复逻辑被替换
- 所有现有测试通过
- 无功能回退

## 7. 风险与缓解

### 7.1 风险

1. **重构破坏现有功能**
   - 缓解：每阶段完成后运行测试
   - 缓解：保持函数签名兼容

2. **测试覆盖不足**
   - 缓解：强制要求每个函数至少 3 个测试用例
   - 缓解：使用覆盖率工具检查

3. **性能影响**
   - 缓解：工具函数应为纯函数，无副作用
   - 缓解：避免不必要的抽象

### 7.2 依赖风险

- 无外部依赖风险
- 所有功能基于 Python 标准库

## 8. 时间估算

### 8.1 开发时间

- 第一阶段（基础工具）：2-3 小时
- 第二阶段（专用工具）：1-2 小时
- 第三阶段（报告工具）：2-3 小时
- 测试编写：3-4 小时
- 重构现有代码：2-3 小时

**总计**：10-15 小时

### 8.2 里程碑

1. 基础工具完成并测试通过
2. 专用工具完成并测试通过
3. 报告工具完成并测试通过
4. 现有代码重构完成
5. 全量测试通过

## 9. 后续扩展

### 9.1 可能的扩展

1. **缓存工具**：添加 LLM 响应缓存
2. **重试机制**：添加 API 调用重试
3. **性能监控**：添加函数执行时间监控
4. **配置验证**：添加配置文件验证

### 9.2 扩展原则

- 新功能应遵循单一职责原则
- 新功能应有完整的测试覆盖
- 新功能应有完整的文档

## 10. 附录

### 10.1 参考文档

- Python 官方文档：https://docs.python.org/3/
- Pytest 官方文档：https://docs.pytest.org/
- ChromaDB 官方文档：https://docs.trychroma.com/

### 10.2 相关文件

- `CLAUDE.md` - 项目开发规范
- `DEVELOPMENT_PROGRESS.md` - 开发进度
- `TECHNICAL_ARCHITECTURE.md` - 技术架构
