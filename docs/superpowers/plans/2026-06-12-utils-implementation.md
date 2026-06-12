# Utils 模块实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 utils/ 工具模块，提取项目中的通用功能，消除代码重复

**Architecture:** 创建 7 个工具文件（llm_parser, report_helpers, text_utils, metadata_utils, date_utils, json_utils, logger），每个文件专注于一个功能领域，然后重构现有代码使用这些工具

**Tech Stack:** Python 3.13+, pytest, logging

---

## 文件结构

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

---

## Task 1: 日志工具 (logger.py)

**Files:**
- Create: `utils/logger.py`
- Create: `utils/tests/test_logger.py`

- [ ] **Step 1: 创建测试文件结构**

```bash
mkdir -p utils/tests
touch utils/tests/__init__.py
```

- [ ] **Step 2: 编写日志工具测试**

```python
# utils/tests/test_logger.py
import logging
import os
import tempfile
from utils.logger import setup_logger, get_logger


class TestSetupLogger:
    """setup_logger 函数测试"""

    def test_setup_logger_returns_logger(self):
        """测试返回正确的 Logger 实例"""
        logger = setup_logger("test_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_setup_logger_with_level(self):
        """测试设置日志级别"""
        logger = setup_logger("test_debug", level=logging.DEBUG)
        assert logger.level == logging.DEBUG

    def test_setup_logger_has_handlers(self):
        """测试日志记录器有处理器"""
        logger = setup_logger("test_handlers")
        assert len(logger.handlers) > 0

    def test_setup_logger_format(self):
        """测试日志格式"""
        logger = setup_logger("test_format")
        handler = logger.handlers[0]
        assert handler.formatter is not None


class TestGetLogger:
    """get_logger 函数测试"""

    def test_get_logger_returns_logger(self):
        """测试返回正确的 Logger 实例"""
        logger = get_logger("test_get")
        assert isinstance(logger, logging.Logger)

    def test_get_logger_same_instance(self):
        """测试相同名称返回相同实例"""
        logger1 = get_logger("test_same")
        logger2 = get_logger("test_same")
        assert logger1 is logger2

    def test_get_logger_auto_setup(self):
        """测试自动配置"""
        logger = get_logger("test_auto")
        assert len(logger.handlers) > 0
```

- [ ] **Step 3: 运行测试验证失败**

```bash
pytest utils/tests/test_logger.py -v
```

Expected: FAIL - `ModuleNotFoundError: No module named 'utils.logger'`

- [ ] **Step 4: 实现日志工具**

```python
# utils/logger.py
import logging
import os
from pathlib import Path


# 已配置的日志记录器缓存
_configured_loggers: set[str] = set()


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    配置日志记录器。

    Args:
        name: 日志记录器名称
        level: 日志级别

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加处理器
    if name in _configured_loggers:
        return logger

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # 文件处理器（可选）
    log_dir = Path("logs")
    try:
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(
            log_dir / "app.log", encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(console_format)
        logger.addHandler(file_handler)
    except (OSError, PermissionError):
        # 文件处理器创建失败时只使用控制台
        pass

    _configured_loggers.add(name)
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器（如果未配置则自动配置）。

    Args:
        name: 日志记录器名称

    Returns:
        日志记录器
    """
    if name not in _configured_loggers:
        return setup_logger(name)
    return logging.getLogger(name)
```

- [ ] **Step 5: 运行测试验证通过**

```bash
pytest utils/tests/test_logger.py -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 6: 提交**

```bash
git add utils/logger.py utils/tests/__init__.py utils/tests/test_logger.py
git commit -m "feat: 添加日志工具 (utils/logger)"
```

---

## Task 2: 日期工具 (date_utils.py)

**Files:**
- Create: `utils/date_utils.py`
- Create: `utils/tests/test_date_utils.py`

- [ ] **Step 1: 编写日期工具测试**

```python
# utils/tests/test_date_utils.py
from datetime import datetime
from unittest.mock import patch
from utils.date_utils import format_datetime, get_current_timestamp


class TestFormatDatetime:
    """format_datetime 函数测试"""

    def test_format_default(self):
        """测试默认格式"""
        dt = datetime(2026, 6, 12, 14, 30)
        result = format_datetime(dt)
        assert result == "2026-06-12 14:30"

    def test_format_custom(self):
        """测试自定义格式"""
        dt = datetime(2026, 6, 12, 14, 30, 0)
        result = format_datetime(dt, "%Y/%m/%d")
        assert result == "2026/06/12"

    def test_format_none_uses_current(self):
        """测试 None 使用当前时间"""
        with patch("utils.date_utils.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 1, 0, 0)
            mock_dt.strftime = datetime.strftime
            result = format_datetime()
            assert "2026-01-01" in result


class TestGetCurrentTimestamp:
    """get_current_timestamp 函数测试"""

    def test_returns_string(self):
        """测试返回字符串"""
        result = get_current_timestamp()
        assert isinstance(result, str)

    def test_iso_format(self):
        """测试 ISO 格式"""
        result = get_current_timestamp()
        # ISO 格式包含 T
        assert "T" in result or "-" in result
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest utils/tests/test_date_utils.py -v
```

Expected: FAIL - `ModuleNotFoundError: No module named 'utils.date_utils'`

- [ ] **Step 3: 实现日期工具**

```python
# utils/date_utils.py
from datetime import datetime


def format_datetime(dt: datetime = None, format_str: str = "%Y-%m-%d %H:%M") -> str:
    """
    格式化日期时间。

    Args:
        dt: datetime 对象，默认为当前时间
        format_str: 格式字符串

    Returns:
        格式化后的日期字符串
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(format_str)


def get_current_timestamp() -> str:
    """
    获取当前时间戳（ISO 格式）。

    Returns:
        ISO 格式的时间戳字符串
    """
    return datetime.now().isoformat()
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest utils/tests/test_date_utils.py -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 5: 提交**

```bash
git add utils/date_utils.py utils/tests/test_date_utils.py
git commit -m "feat: 添加日期工具 (utils/date_utils)"
```

---

## Task 3: JSON 工具 (json_utils.py)

**Files:**
- Create: `utils/json_utils.py`
- Create: `utils/tests/test_json_utils.py`

- [ ] **Step 1: 编写 JSON 工具测试**

```python
# utils/tests/test_json_utils.py
import json
from datetime import datetime
from utils.json_utils import json_serialize, json_dumps_pretty


class TestJsonSerialize:
    """json_serialize 函数测试"""

    def test_serialize_dict(self):
        """测试序列化字典"""
        data = {"name": "测试", "value": 123}
        result = json_serialize(data)
        assert json.loads(result) == data

    def test_serialize_chinese(self):
        """测试中文不转义"""
        data = {"key": "中文内容"}
        result = json_serialize(data)
        assert "中文内容" in result

    def test_serialize_custom_indent(self):
        """测试自定义缩进"""
        data = {"a": 1}
        result = json_serialize(data, indent=4)
        assert "    " in result

    def test_serialize_datetime(self):
        """测试 datetime 序列化"""
        data = {"time": datetime(2026, 1, 1)}
        result = json_serialize(data)
        assert "2026" in result


class TestJsonDumpsPretty:
    """json_dumps_pretty 函数测试"""

    def test_pretty_output(self):
        """测试美化输出"""
        data = {"name": "test", "items": [1, 2, 3]}
        result = json_dumps_pretty(data)
        assert "\n" in result
        assert "test" in result

    def test_pretty_chinese(self):
        """测试中文美化"""
        data = {"key": "中文"}
        result = json_dumps_pretty(data)
        assert "中文" in result
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest utils/tests/test_json_utils.py -v
```

Expected: FAIL - `ModuleNotFoundError: No module named 'utils.json_utils'`

- [ ] **Step 3: 实现 JSON 工具**

```python
# utils/json_utils.py
import json


def json_serialize(obj: any, indent: int = 2) -> str:
    """
    JSON 序列化，处理中文和特殊类型。

    Args:
        obj: 要序列化的对象
        indent: 缩进空格数

    Returns:
        JSON 字符串
    """
    return json.dumps(obj, ensure_ascii=False, indent=indent, default=str)


def json_dumps_pretty(obj: any) -> str:
    """
    美化 JSON 输出。

    Args:
        obj: 要序列化的对象

    Returns:
        美化后的 JSON 字符串
    """
    return json.dumps(obj, ensure_ascii=False, indent=2, default=str)
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest utils/tests/test_json_utils.py -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 5: 提交**

```bash
git add utils/json_utils.py utils/tests/test_json_utils.py
git commit -m "feat: 添加 JSON 工具 (utils/json_utils)"
```

---

## Task 4: 文本工具 (text_utils.py)

**Files:**
- Create: `utils/text_utils.py`
- Create: `utils/tests/test_text_utils.py`

- [ ] **Step 1: 编写文本工具测试**

```python
# utils/tests/test_text_utils.py
from utils.text_utils import clean_text, split_text


class TestCleanText:
    """clean_text 函数测试"""

    def test_clean_whitespace(self):
        """测试清理多余空白"""
        text = "hello   world"
        result = clean_text(text)
        assert result == "hello world"

    def test_clean_newlines(self):
        """测试清理多余换行"""
        text = "hello\n\n\nworld"
        result = clean_text(text)
        assert "\n\n" in result
        assert "\n\n\n" not in result

    def test_clean_strip(self):
        """测试首尾空格"""
        text = "  hello  "
        result = clean_text(text)
        assert result == "hello"

    def test_clean_tabs(self):
        """测试制表符"""
        text = "hello\t\tworld"
        result = clean_text(text)
        assert "\t\t" not in result


class TestSplitText:
    """split_text 函数测试"""

    def test_short_text(self):
        """测试短文本不分块"""
        text = "short text"
        result = split_text(text, chunk_size=100)
        assert result == [text]

    def test_long_text(self):
        """测试长文本分块"""
        text = "a" * 2000
        result = split_text(text, chunk_size=1000, overlap=100)
        assert len(result) > 1

    def test_overlap(self):
        """测试重叠"""
        text = "a" * 2000
        result = split_text(text, chunk_size=1000, overlap=200)
        assert len(result) >= 2

    def test_empty_text(self):
        """测试空文本"""
        result = split_text("")
        assert result == []

    def test_sentence_boundary(self):
        """测试句子边界分割"""
        text = "第一句话。第二句话。第三句话。" * 100
        result = split_text(text, chunk_size=100, overlap=20)
        assert len(result) > 1
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest utils/tests/test_text_utils.py -v
```

Expected: FAIL - `ModuleNotFoundError: No module named 'utils.text_utils'`

- [ ] **Step 3: 实现文本工具**

```python
# utils/text_utils.py
import re


def clean_text(text: str) -> str:
    """
    清洗文本：去除多余空白、特殊字符。

    Args:
        text: 原始文本

    Returns:
        清洗后的文本
    """
    # 合并多个空白为单个空格
    text = re.sub(r'\s+', ' ', text)
    # 规范化换行符
    text = re.sub(r'\n\s*\n', '\n\n', text)
    # 合并非换行空白
    text = re.sub(r'[^\S\n]+', ' ', text)
    return text.strip()


def split_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
    """
    将文本分块，支持句子边界分割。

    Args:
        text: 原始文本
        chunk_size: 块大小（字符数）
        overlap: 重叠字符数

    Returns:
        文本块列表
    """
    if not text or not text.strip():
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    separators = ["\n\n", "\n", "。", ".", "！", "!", "？", "?"]

    while start < len(text):
        end = start + chunk_size

        if end >= len(text):
            chunks.append(text[start:].strip())
            break

        # 尝试在句子边界分割
        chunk = text[start:end]
        last_sep = -1

        for sep in separators:
            pos = chunk.rfind(sep)
            if pos > chunk_size * 0.3 and pos > last_sep:
                last_sep = pos

        if last_sep > 0:
            end = start + last_sep + len(sep)

        chunks.append(text[start:end].strip())
        start = end - overlap

    return [c for c in chunks if c]
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest utils/tests/test_text_utils.py -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 5: 提交**

```bash
git add utils/text_utils.py utils/tests/test_text_utils.py
git commit -m "feat: 添加文本工具 (utils/text_utils)"
```

---

## Task 5: LLM JSON 解析工具 (llm_parser.py)

**Files:**
- Create: `utils/llm_parser.py`
- Create: `utils/tests/test_llm_parser.py`

- [ ] **Step 1: 编写 LLM 解析工具测试**

```python
# utils/tests/test_llm_parser.py
import json
from utils.llm_parser import extract_json_from_llm


class TestExtractJsonFromLlm:
    """extract_json_from_llm 函数测试"""

    def test_pure_json(self):
        """测试纯 JSON"""
        data = {"key": "value"}
        content = json.dumps(data)
        result = extract_json_from_llm(content)
        assert result == data

    def test_json_in_code_block(self):
        """测试 markdown 代码块包裹的 JSON"""
        data = {"key": "value"}
        content = f"```json\n{json.dumps(data)}\n```"
        result = extract_json_from_llm(content)
        assert result == data

    def test_json_in_generic_code_block(self):
        """测试普通代码块包裹的 JSON"""
        data = {"key": "value"}
        content = f"```\n{json.dumps(data)}\n```"
        result = extract_json_from_llm(content)
        assert result == data

    def test_json_with_surrounding_text(self):
        """测试包含其他文本的 JSON"""
        data = {"key": "value"}
        content = f"这是分析结果：\n{json.dumps(data)}\n以上是结果。"
        result = extract_json_from_llm(content)
        assert result == data

    def test_invalid_json(self):
        """测试无效 JSON"""
        result = extract_json_from_llm("这不是JSON")
        assert result is None

    def test_json_array(self):
        """测试 JSON 数组"""
        data = [1, 2, 3]
        content = json.dumps(data)
        result = extract_json_from_llm(content)
        assert result == data

    def test_empty_string(self):
        """测试空字符串"""
        result = extract_json_from_llm("")
        assert result is None
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest utils/tests/test_llm_parser.py -v
```

Expected: FAIL - `ModuleNotFoundError: No module named 'utils.llm_parser'`

- [ ] **Step 3: 实现 LLM 解析工具**

```python
# utils/llm_parser.py
import json
import re


def extract_json_from_llm(response: str) -> dict | list | None:
    """
    从 LLM 响应中提取 JSON。

    处理情况：
    1. 纯 JSON 字符串
    2. markdown 代码块包裹的 JSON（```json ... ```）
    3. 包含其他文本的 JSON

    Args:
        response: LLM 响应文本

    Returns:
        解析后的 dict/list，失败返回 None
    """
    if not response or not response.strip():
        return None

    content = response.strip()

    # 尝试从 markdown 代码块提取
    if "```json" in content:
        try:
            json_str = content.split("```json")[1].split("```")[0].strip()
            return json.loads(json_str)
        except (IndexError, json.JSONDecodeError):
            pass

    # 尝试从普通代码块提取
    if "```" in content:
        try:
            json_str = content.split("```")[1].split("```")[0].strip()
            return json.loads(json_str)
        except (IndexError, json.JSONDecodeError):
            pass

    # 尝试直接解析
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # 尝试查找 JSON 对象或数组
    try:
        # 查找第一个 { 或 [ 到最后一个 } 或 ]
        for start_char, end_char in [('{', '}'), ('[', ']')]:
            start = content.find(start_char)
            end = content.rfind(end_char)
            if start != -1 and end != -1 and end > start:
                json_str = content[start:end + 1]
                return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    return None
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest utils/tests/test_llm_parser.py -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 5: 提交**

```bash
git add utils/llm_parser.py utils/tests/test_llm_parser.py
git commit -m "feat: 添加 LLM JSON 解析工具 (utils/llm_parser)"
```

---

## Task 6: 元数据工具 (metadata_utils.py)

**Files:**
- Create: `utils/metadata_utils.py`
- Create: `utils/tests/test_metadata_utils.py`

- [ ] **Step 1: 编写元数据工具测试**

```python
# utils/tests/test_metadata_utils.py
import json
from utils.metadata_utils import sanitize_metadata, sanitize_metadatas


class TestSanitizeMetadata:
    """sanitize_metadata 函数测试"""

    def test_list_to_string(self):
        """测试 list 转字符串"""
        meta = {"tags": ["a", "b", "c"]}
        result = sanitize_metadata(meta)
        assert result["tags"] == "a, b, c"

    def test_dict_to_string(self):
        """测试 dict 转 JSON 字符串"""
        meta = {"info": {"key": "value"}}
        result = sanitize_metadata(meta)
        assert json.loads(result["info"]) == {"key": "value"}

    def test_none_to_empty(self):
        """测试 None 转空字符串"""
        meta = {"field": None}
        result = sanitize_metadata(meta)
        assert result["field"] == ""

    def test_string_unchanged(self):
        """测试字符串保持不变"""
        meta = {"name": "test"}
        result = sanitize_metadata(meta)
        assert result["name"] == "test"

    def test_number_unchanged(self):
        """测试数字保持不变"""
        meta = {"count": 42}
        result = sanitize_metadata(meta)
        assert result["count"] == 42


class TestSanitizeMetadatas:
    """sanitize_metadatas 函数测试"""

    def test_multiple_metadatas(self):
        """测试多个元数据"""
        metadatas = [
            {"tags": ["a", "b"]},
            {"info": {"key": "value"}}
        ]
        result = sanitize_metadatas(metadatas)
        assert len(result) == 2
        assert result[0]["tags"] == "a, b"

    def test_empty_list(self):
        """测试空列表"""
        result = sanitize_metadatas([])
        assert result == []
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest utils/tests/test_metadata_utils.py -v
```

Expected: FAIL - `ModuleNotFoundError: No module named 'utils.metadata_utils'`

- [ ] **Step 3: 实现元数据工具**

```python
# utils/metadata_utils.py
import json


def sanitize_metadata(metadata: dict) -> dict:
    """
    清洗单个元数据，确保 ChromaDB 兼容。

    处理：
    1. list -> 逗号分隔字符串
    2. dict -> JSON 字符串
    3. None -> 空字符串
    4. 其他类型保持不变

    Args:
        metadata: 原始元数据字典

    Returns:
        清洗后的元数据字典
    """
    cleaned = {}
    for key, value in metadata.items():
        if isinstance(value, list):
            cleaned[key] = ", ".join(str(item) for item in value)
        elif isinstance(value, dict):
            cleaned[key] = json.dumps(value, ensure_ascii=False)
        elif value is None:
            cleaned[key] = ""
        else:
            cleaned[key] = value
    return cleaned


def sanitize_metadatas(metadatas: list[dict]) -> list[dict]:
    """
    批量清洗元数据。

    Args:
        metadatas: 元数据字典列表

    Returns:
        清洗后的元数据字典列表
    """
    return [sanitize_metadata(meta) for meta in metadatas]
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest utils/tests/test_metadata_utils.py -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 5: 提交**

```bash
git add utils/metadata_utils.py utils/tests/test_metadata_utils.py
git commit -m "feat: 添加元数据工具 (utils/metadata_utils)"
```

---

## Task 7: 报告工具 (report_helpers.py)

**Files:**
- Create: `utils/report_helpers.py`
- Create: `utils/tests/test_report_helpers.py`

- [ ] **Step 1: 编写报告工具测试**

```python
# utils/tests/test_report_helpers.py
from datetime import datetime
from unittest.mock import patch
from utils.report_helpers import (
    generate_report_header,
    prepare_analysis_data,
    generate_fallback_report,
)


class TestGenerateReportHeader:
    """generate_report_header 函数测试"""

    def test_basic_header(self):
        """测试基本报告头部"""
        result = generate_report_header(
            title="测试报告",
            competitors=["竞品A", "竞品B"],
            report_type="quick"
        )
        assert "测试报告" in result
        assert "竞品A" in result
        assert "竞品B" in result
        assert "快速" in result

    def test_report_types(self):
        """测试所有报告类型"""
        for rtype, cn_name in [("quick", "快速"), ("standard", "标准"), ("deep", "深度")]:
            result = generate_report_header("标题", ["A"], rtype)
            assert cn_name in result


class TestPrepareAnalysisData:
    """prepare_analysis_data 函数测试"""

    def test_returns_string(self):
        """测试返回字符串"""
        data = {"key": "value"}
        result = prepare_analysis_data(data)
        assert isinstance(result, str)

    def test_contains_original_keys(self):
        """测试包含原始键"""
        data = {"competitors": ["A"], "summary": "test"}
        result = prepare_analysis_data(data)
        assert "competitors" in result
        assert "summary" in result


class TestGenerateFallbackReport:
    """generate_fallback_report 函数测试"""

    def test_contains_competitor_name(self):
        """测试包含竞品名称"""
        data = {
            "feature_matrix": {"features": []},
            "pricing_comparison": {"competitors": {}},
            "swot_analysis": {}
        }
        result = generate_fallback_report("测试竞品", data)
        assert "测试竞品" in result

    def test_contains_features(self):
        """测试包含功能信息"""
        data = {
            "feature_matrix": {
                "features": [
                    {"name": "功能A", "description": "描述A"}
                ]
            },
            "pricing_comparison": {"competitors": {}},
            "swot_analysis": {}
        }
        result = generate_fallback_report("竞品", data)
        assert "功能A" in result
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest utils/tests/test_report_helpers.py -v
```

Expected: FAIL - `ModuleNotFoundError: No module named 'utils.report_helpers'`

- [ ] **Step 3: 实现报告工具**

```python
# utils/report_helpers.py
import json
from datetime import datetime

from utils.date_utils import format_datetime
from utils.json_utils import json_serialize


# 报告类型中文映射
REPORT_TYPE_NAMES = {
    "quick": "快速",
    "standard": "标准",
    "deep": "深度",
}


def generate_report_header(
    title: str,
    competitors: list[str],
    report_type: str
) -> str:
    """
    生成报告头部。

    Args:
        title: 报告标题
        competitors: 竞品名称列表
        report_type: 报告类型（quick/standard/deep）

    Returns:
        Markdown 格式的报告头部
    """
    type_name = REPORT_TYPE_NAMES.get(report_type, report_type)
    now = format_datetime()

    header = f"""# {title}

**生成时间**: {now}
**分析类型**: {type_name}
**分析竞品数量**: {len(competitors)}

## 分析竞品

"""
    for i, name in enumerate(competitors, 1):
        header += f"{i}. {name}\n"

    return header


def prepare_analysis_data(analysis_result: dict) -> str:
    """
    准备报告数据，将分析结果转换为 JSON 字符串。

    Args:
        analysis_result: 分析结果字典

    Returns:
        JSON 格式的报告数据
    """
    return json_serialize(analysis_result)


def generate_fallback_report(
    competitor_name: str,
    analysis_data: dict
) -> str:
    """
    生成降级报告（当 LLM 失败时）。

    Args:
        competitor_name: 竞品名称
        analysis_data: 分析数据

    Returns:
        简化的 Markdown 报告
    """
    header = generate_report_header(
        title=f"{competitor_name} 竞品分析报告",
        competitors=[competitor_name],
        report_type="quick"
    )

    sections = [header]

    # 分析摘要
    summary = analysis_data.get("analysis_summary", "")
    if summary:
        sections.append(f"## 分析摘要\n\n{summary}\n")

    # 功能矩阵
    feature_matrix = analysis_data.get("feature_matrix", {})
    features = feature_matrix.get("features", [])[:10]
    if features:
        sections.append("## 主要功能\n")
        for f in features:
            name = f.get("name", "未知功能")
            desc = f.get("description", "")
            sections.append(f"- **{name}**: {desc}")
        sections.append("")

    # 定价对比
    pricing = analysis_data.get("pricing_comparison", {})
    competitors_pricing = pricing.get("competitors", {})
    if competitors_pricing:
        sections.append("## 定价信息\n")
        for comp, info in competitors_pricing.items():
            if isinstance(info, dict):
                price = info.get("price", "未知")
                sections.append(f"- **{comp}**: {price}")
            else:
                sections.append(f"- **{comp}**: {info}")
        sections.append("")

    # SWOT 分析
    swot = analysis_data.get("swot_analysis", {})
    if swot:
        sections.append("## SWOT 分析\n")
        for item in swot.get("strengths", [])[:3]:
            if isinstance(item, str):
                sections.append(f"- 优势: {item}")
        for item in swot.get("weaknesses", [])[:3]:
            if isinstance(item, str):
                sections.append(f"- 劣势: {item}")
        sections.append("")

    # 时间戳
    sections.append(f"\n---\n*报告生成时间: {format_datetime()}*\n")

    return "\n".join(sections)
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest utils/tests/test_report_helpers.py -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 5: 提交**

```bash
git add utils/report_helpers.py utils/tests/test_report_helpers.py
git commit -m "feat: 添加报告工具 (utils/report_helpers)"
```

---

## Task 8: 模块导出 (__init__.py)

**Files:**
- Create: `utils/__init__.py` (已存在，需要更新)

- [ ] **Step 1: 更新模块导出**

```python
# utils/__init__.py
"""
工具模块 - 提供通用工具函数
"""

from utils.logger import setup_logger, get_logger
from utils.date_utils import format_datetime, get_current_timestamp
from utils.json_utils import json_serialize, json_dumps_pretty
from utils.text_utils import clean_text, split_text
from utils.llm_parser import extract_json_from_llm
from utils.metadata_utils import sanitize_metadata, sanitize_metadatas
from utils.report_helpers import (
    generate_report_header,
    prepare_analysis_data,
    generate_fallback_report,
    REPORT_TYPE_NAMES,
)

__all__ = [
    # 日志
    "setup_logger",
    "get_logger",
    # 日期
    "format_datetime",
    "get_current_timestamp",
    # JSON
    "json_serialize",
    "json_dumps_pretty",
    # 文本
    "clean_text",
    "split_text",
    # LLM 解析
    "extract_json_from_llm",
    # 元数据
    "sanitize_metadata",
    "sanitize_metadatas",
    # 报告
    "generate_report_header",
    "prepare_analysis_data",
    "generate_fallback_report",
    "REPORT_TYPE_NAMES",
]
```

- [ ] **Step 2: 运行全部测试**

```bash
pytest utils/tests/ -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 3: 提交**

```bash
git add utils/__init__.py
git commit -m "feat: 更新 utils 模块导出"
```

---

## Task 9: 重构 - 替换 planner.py 中的 JSON 解析

**Files:**
- Modify: `agent/nodes/planner.py`

- [ ] **Step 1: 读取现有代码**

```bash
cat agent/nodes/planner.py
```

- [ ] **Step 2: 添加 import**

在文件顶部添加：
```python
from utils.llm_parser import extract_json_from_llm
```

- [ ] **Step 3: 替换 JSON 解析代码**

将：
```python
if "```json" in content:
    json_str = content.split("```json")[1].split("```")[0].strip()
elif "```" in content:
    json_str = content.split("```")[1].split("```")[0].strip()
else:
    json_str = content.strip()
plan = json.loads(json_str)
```

替换为：
```python
plan = extract_json_from_llm(content)
if plan is None:
    raise json.JSONDecodeError("无法解析 JSON", content, 0)
```

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_agent.py -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 5: 提交**

```bash
git add agent/nodes/planner.py
git commit -m "refactor: planner.py 使用 utils.llm_parser"
```

---

## Task 10: 重构 - 替换 extractor.py 中的 JSON 解析

**Files:**
- Modify: `agent/nodes/extractor.py`

- [ ] **Step 1: 读取现有代码**

```bash
cat agent/nodes/extractor.py
```

- [ ] **Step 2: 添加 import**

在文件顶部添加：
```python
from utils.llm_parser import extract_json_from_llm
```

- [ ] **Step 3: 替换 JSON 解析代码**

将：
```python
if "```json" in content:
    json_str = content.split("```json")[1].split("```")[0].strip()
elif "```" in content:
    json_str = content.split("```")[1].split("```")[0].strip()
else:
    json_str = content.strip()
info = json.loads(json_str)
```

替换为：
```python
info = extract_json_from_llm(content)
if info is None:
    info = {"raw_response": content}
```

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_agent.py -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 5: 提交**

```bash
git add agent/nodes/extractor.py
git commit -m "refactor: extractor.py 使用 utils.llm_parser"
```

---

## Task 11: 重构 - 替换 reporter.py 中的报告工具

**Files:**
- Modify: `agent/nodes/reporter.py`

- [ ] **Step 1: 读取现有代码**

```bash
cat agent/nodes/reporter.py
```

- [ ] **Step 2: 添加 import**

在文件顶部添加：
```python
from utils.report_helpers import (
    generate_report_header,
    prepare_analysis_data,
    generate_fallback_report,
)
from utils.json_utils import json_serialize
```

- [ ] **Step 3: 替换 _generate_header 方法**

将 `_generate_header` 方法替换为调用 `generate_report_header`。

- [ ] **Step 4: 替换 _prepare_analysis_data 方法**

将 `_prepare_analysis_data` 方法替换为调用 `prepare_analysis_data`。

- [ ] **Step 5: 替换 _generate_simple_report 方法**

将 `_generate_simple_report` 方法替换为调用 `generate_fallback_report`。

- [ ] **Step 6: 运行测试**

```bash
pytest tests/test_agent.py tests/test_report.py -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 7: 提交**

```bash
git add agent/nodes/reporter.py
git commit -m "refactor: reporter.py 使用 utils.report_helpers"
```

---

## Task 12: 重构 - 替换 generator.py 中的报告工具

**Files:**
- Modify: `report/generator.py`

- [ ] **Step 1: 读取现有代码**

```bash
cat report/generator.py
```

- [ ] **Step 2: 添加 import**

在文件顶部添加：
```python
from utils.report_helpers import (
    generate_report_header,
    prepare_analysis_data,
    generate_fallback_report,
)
from utils.json_utils import json_serialize
```

- [ ] **Step 3: 替换 _generate_header 方法**

将 `_generate_header` 方法替换为调用 `generate_report_header`。

- [ ] **Step 4: 替换 _prepare_data 方法**

将 `_prepare_data` 方法替换为调用 `prepare_analysis_data`。

- [ ] **Step 5: 替换 _generate_fallback 方法**

将 `_generate_fallback` 方法替换为调用 `generate_fallback_report`。

- [ ] **Step 6: 运行测试**

```bash
pytest tests/test_report.py -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 7: 提交**

```bash
git add report/generator.py
git commit -m "refactor: generator.py 使用 utils.report_helpers"
```

---

## Task 13: 重构 - 替换 cleaner.py 中的文本清洗

**Files:**
- Modify: `collector/cleaner.py`

- [ ] **Step 1: 读取现有代码**

```bash
cat collector/cleaner.py
```

- [ ] **Step 2: 添加 import**

在文件顶部添加：
```python
from utils.text_utils import clean_text as utils_clean_text
```

- [ ] **Step 3: 替换 clean_text 方法**

将 `clean_text` 静态方法替换为调用 `utils_clean_text`。

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_collector.py -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 5: 提交**

```bash
git add collector/cleaner.py
git commit -m "refactor: cleaner.py 使用 utils.text_utils"
```

---

## Task 14: 重构 - 替换 web_scraper.py 中的文本清洗

**Files:**
- Modify: `collector/web_scraper.py`

- [ ] **Step 1: 读取现有代码**

```bash
cat collector/web_scraper.py
```

- [ ] **Step 2: 添加 import**

在文件顶部添加：
```python
from utils.text_utils import clean_text as utils_clean_text
```

- [ ] **Step 3: 替换 clean 方法**

将 `clean` 方法替换为调用 `utils_clean_text`。

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_collector.py -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 5: 提交**

```bash
git add collector/web_scraper.py
git commit -m "refactor: web_scraper.py 使用 utils.text_utils"
```

---

## Task 15: 重构 - 替换 knowledge_base.py 中的文本分块

**Files:**
- Modify: `knowledge/knowledge_base.py`

- [ ] **Step 1: 读取现有代码**

```bash
cat knowledge/knowledge_base.py
```

- [ ] **Step 2: 添加 import**

在文件顶部添加：
```python
from utils.text_utils import split_text as utils_split_text
```

- [ ] **Step 3: 替换 _split_text 方法**

将 `_split_text` 方法替换为调用 `utils_split_text`。

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_knowledge_simple.py -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 5: 提交**

```bash
git add knowledge/knowledge_base.py
git commit -m "refactor: knowledge_base.py 使用 utils.text_utils"
```

---

## Task 16: 重构 - 替换 vector_store.py 中的元数据清洗

**Files:**
- Modify: `knowledge/vector_store.py`

- [ ] **Step 1: 读取现有代码**

```bash
cat knowledge/vector_store.py
```

- [ ] **Step 2: 添加 import**

在文件顶部添加：
```python
from utils.metadata_utils import sanitize_metadatas
```

- [ ] **Step 3: 替换 add_documents 中的元数据清洗**

将 `add_documents` 中的元数据清洗循环替换为调用 `sanitize_metadatas`。

- [ ] **Step 4: 替换 update_documents 中的元数据清洗**

将 `update_documents` 中的元数据清洗循环替换为调用 `sanitize_metadatas`。

- [ ] **Step 5: 运行测试**

```bash
pytest tests/test_knowledge_simple.py -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 6: 提交**

```bash
git add knowledge/vector_store.py
git commit -m "refactor: vector_store.py 使用 utils.metadata_utils"
```

---

## Task 17: 全量测试

**Files:**
- None (测试现有代码)

- [ ] **Step 1: 运行所有测试**

```bash
pytest tests/test_models.py tests/test_knowledge_simple.py tests/test_collector.py tests/test_agent.py tests/test_report.py tests/test_api.py utils/tests/ -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 2: 检查测试覆盖率**

```bash
pytest utils/tests/ -v --cov=utils --cov-report=term-missing
```

Expected: 90%+ 覆盖率

- [ ] **Step 3: 提交最终版本**

```bash
git add -A
git commit -m "feat: 完成 utils 模块开发和重构"
```

---

## 完成检查清单

- [ ] 所有 7 个工具文件实现完成
- [ ] 所有 7 个测试文件编写完成
- [ ] 所有测试通过
- [ ] 测试覆盖率 90%+
- [ ] 现有代码重构完成
- [ ] 无功能回退
- [ ] 文档已更新（CLAUDE.md, DEVELOPMENT_PROGRESS.md）
