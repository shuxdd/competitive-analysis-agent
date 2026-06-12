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
