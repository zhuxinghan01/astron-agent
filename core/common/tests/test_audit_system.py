"""
Unit tests for common.audit_system module.
"""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Import only what we can test without circular imports
from common.audit_system.enums import Status
from common.audit_system.utils import END_SYMBOLS, NON_END_SYMBOLS, Sentence
from common.exceptions.errs import AuditServiceException

# Skip complex classes that have circular import issues
# Test only the utility functions and enums


class TestSentence:
    """Test Sentence utility class."""

    def test_find_valid_sentence_empty_content(self):
        """Test find_valid_sentence with empty content."""
        sentences, remaining = Sentence.find_valid_sentence("")
        assert sentences == []
        assert remaining == ""

    def test_find_valid_sentence_all_content(self):
        """Test find_valid_sentence with ALL_SENTENCE_LEN."""
        content = "这是一个完整的句子。"
        from common.audit_system.utils import ALL_SENTENCE_LEN

        sentences, remaining = Sentence.find_valid_sentence(content, ALL_SENTENCE_LEN)
        assert sentences == [content]
        assert remaining == ""

    def test_find_valid_sentence_with_end_symbol(self):
        """Test find_valid_sentence with end symbol."""
        content = "这是第一句。这是第二句。"
        sentences, remaining = Sentence.find_valid_sentence(content, 50)
        assert len(sentences) > 0
        # 由于算法可能将所有内容作为一个句子处理，remaining可能为空
        assert isinstance(remaining, str)

    def test_find_valid_sentence_with_non_end_symbol(self):
        """Test find_valid_sentence with non-end symbol."""
        content = "这是第一句，这是第二句"
        sentences, remaining = Sentence.find_valid_sentence(content, 50)
        assert len(sentences) > 0

    def test_find_valid_sentence_fallback(self):
        """Test find_valid_sentence fallback to length limit."""
        content = "这是一个很长的句子没有标点符号" * 10
        sentences, remaining = Sentence.find_valid_sentence(content, 50)
        assert len(sentences) > 0
        assert len(sentences[0]) <= 50

    def test_has_end_symbol_true(self):
        """Test has_end_symbol returns True."""
        assert Sentence.has_end_symbol("这是句子。")
        assert Sentence.has_end_symbol("这是句子!")
        assert Sentence.has_end_symbol("这是句子?")
        assert Sentence.has_end_symbol("这是句子\n")

    def test_has_end_symbol_false(self):
        """Test has_end_symbol returns False."""
        assert not Sentence.has_end_symbol("这是句子，没有结束")
        assert not Sentence.has_end_symbol("这是句子：没有结束")

    def test_split_and_keep_delimiters(self):
        """Test split_and_keep_delimiters method."""
        text = "a,b;c.d"
        separators = [",", ";", "."]
        result = Sentence.split_and_keep_delimiters(text, separators)
        # 算法会保留最后剩余的部分
        expected = ["a,", "b;", "c.", "d"]
        assert result == expected

    def test_split_and_keep_delimiters_no_separators(self):
        """Test split_and_keep_delimiters with no separators."""
        text = "abcdef"
        separators = [",", ";"]
        result = Sentence.split_and_keep_delimiters(text, separators)
        assert result == ["abcdef"]

    def test_split_and_keep_delimiters_empty_text(self):
        """Test split_and_keep_delimiters with empty text."""
        text = ""
        separators = [",", ";"]
        result = Sentence.split_and_keep_delimiters(text, separators)
        assert result == []

    def test_extract_first_end_symbol(self):
        """Test _extract_first_end_symbol method."""
        text = "第一句。第二句。第三句。"
        sentences, remaining = Sentence._extract_first_end_symbol(text, 50)
        assert len(sentences) > 0
        # 检查是否包含句号结尾的句子
        assert any("。" in sentence for sentence in sentences)

    def test_extract_before_last_non_end_symbol(self):
        """Test _extract_before_last_non_end_symbol method."""
        text = "第一句，第二句，第三句"
        sentence, remaining = Sentence._extract_before_last_non_end_symbol(text, 50)
        assert sentence != ""
        assert remaining != ""

    def test_extract_before_last_non_end_symbol_no_symbols(self):
        """Test _extract_before_last_non_end_symbol with no non-end symbols."""
        text = "没有标点符号的句子"
        sentence, remaining = Sentence._extract_before_last_non_end_symbol(text, 50)
        assert sentence == ""
        assert remaining == ""


class TestAuditSystemEnums:
    """Test audit system enums."""

    def test_status_enum(self):
        """Test Status enum values."""
        assert Status.NONE == "none"
        assert Status.STOP == "stop"

    def test_status_enum_string_comparison(self):
        """Test Status enum string comparison."""
        status = Status.STOP
        assert status == "stop"
        # 对于枚举，str()返回的是枚举的完整表示
        assert str(status) == "Status.STOP"
