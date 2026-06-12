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
