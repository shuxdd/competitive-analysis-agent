import json


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
