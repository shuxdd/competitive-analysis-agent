import re


def clean_text(text: str) -> str:
    """
    清洗文本：去除多余空白、特殊字符。

    Args:
        text: 原始文本

    Returns:
        清洗后的文本
    """
    # 规范化换行符（先处理，保留段落结构）
    text = re.sub(r'\n\s*\n', '\n\n', text)
    # 合并非换行空白为单个空格
    text = re.sub(r'[^\S\n]+', ' ', text)
    # 清理行首行尾空格
    text = re.sub(r' *\n *', '\n', text)
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
        last_sep_len = 0

        for sep in separators:
            pos = chunk.rfind(sep)
            if pos > chunk_size * 0.3 and pos > last_sep:
                last_sep = pos
                last_sep_len = len(sep)

        if last_sep > 0:
            end = start + last_sep + last_sep_len

        chunks.append(text[start:end].strip())
        start = end - overlap

    return [c for c in chunks if c]
