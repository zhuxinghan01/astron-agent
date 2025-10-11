"""Unit tests for API types module."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import base64
from unittest.mock import patch, Mock
from fastapi import HTTPException
from pydantic import ValidationError

from api.schema.types import (
    GenText2Img,
    SuccessDataResponse,
    ErrorResponse,
    ErrorCResponse,
    OCRLLM,
    ImageGenerate,
    TTSInput,
    SmartTTSInput,
    ImageUnderstandingInput,
    ArXivInput,
    TTIInput,
    ISEInput,
    validate_english
)


class TestGenText2Img:
    """Test cases for GenText2Img model."""

    def test_gentext2img_creation(self):
        """Test GenText2Img model creation."""
        model = GenText2Img(content="test image")
        assert model.content == "test image"
        assert model.width == 1024
        assert model.height == 1024

    def test_gentext2img_custom_dimensions(self):
        """Test GenText2Img with custom dimensions."""
        model = GenText2Img(content="test", width=512, height=768)
        assert model.content == "test"
        assert model.width == 512
        assert model.height == 768

    def test_gentext2img_validation(self):
        """Test GenText2Img validation."""
        with pytest.raises(ValidationError):
            GenText2Img()  # Missing required content


class TestSuccessDataResponse:
    """Test cases for SuccessDataResponse class."""

    def test_success_response_basic(self):
        """Test basic success response creation."""
        data = {"result": "success"}
        response = SuccessDataResponse(data)

        assert response.code == 0
        assert response.data == data
        assert response.message == "success"

    def test_success_response_custom_message(self):
        """Test success response with custom message."""
        data = {"result": "test"}
        response = SuccessDataResponse(data, message="custom message")

        assert response.code == 0
        assert response.data == data
        assert response.message == "custom message"

    def test_success_response_with_sid(self):
        """Test success response with session ID."""
        data = {"result": "test"}
        response = SuccessDataResponse(data, sid="test_sid_123")

        assert response.code == 0
        assert response.data == data
        assert response.message == "success"
        assert response.sid == "test_sid_123"

    def test_success_response_none_data(self):
        """Test success response with None data."""
        response = SuccessDataResponse(None)

        assert response.code == 0
        assert response.data is None
        assert response.message == "success"


class TestErrorResponse:
    """Test cases for ErrorResponse class."""

    def test_error_response_basic(self):
        """Test basic error response creation."""
        # Mock error enum
        mock_enum = Mock()
        mock_enum.code = 500
        mock_enum.msg = "Internal error"

        response = ErrorResponse(mock_enum)

        assert response.code == 500
        assert response.message == "Internal error"

    def test_error_response_with_sid(self):
        """Test error response with session ID."""
        mock_enum = Mock()
        mock_enum.code = 404
        mock_enum.msg = "Not found"

        response = ErrorResponse(mock_enum, sid="test_sid")

        assert response.code == 404
        assert response.message == "Not found"
        assert response.sid == "test_sid"

    def test_error_response_with_custom_message(self):
        """Test error response with custom message."""
        mock_enum = Mock()
        mock_enum.code = 400
        mock_enum.msg = "Bad request"

        response = ErrorResponse(mock_enum, message="Additional details")

        assert response.code == 400
        assert response.message == "Bad request(Additional details)"

    def test_error_response_with_sid_and_message(self):
        """Test error response with both SID and custom message."""
        mock_enum = Mock()
        mock_enum.code = 403
        mock_enum.msg = "Forbidden"

        response = ErrorResponse(mock_enum, sid="test_sid", message="Access denied")

        assert response.code == 403
        assert response.message == "Forbidden(Access denied)"
        assert response.sid == "test_sid"


class TestErrorCResponse:
    """Test cases for ErrorCResponse class."""

    def test_error_c_response_basic(self):
        """Test basic ErrorCResponse creation."""
        response = ErrorCResponse(code=500, message="Server error")

        assert response.code == 500
        assert response.message == "Server error"

    def test_error_c_response_with_sid(self):
        """Test ErrorCResponse with session ID."""
        response = ErrorCResponse(code=404, message="Not found", sid="test_sid")

        assert response.code == 404
        assert response.message == "Not found"
        assert response.sid == "test_sid"

    def test_error_c_response_none_message(self):
        """Test ErrorCResponse with None message."""
        response = ErrorCResponse(code=500, message=None)

        assert response.code == 500
        assert response.message is None


class TestOCRLLM:
    """Test cases for OCRLLM model."""

    def test_ocrllm_basic(self):
        """Test basic OCRLLM creation."""
        model = OCRLLM(file_url="https://example.com/file.pdf")

        assert model.file_url == "https://example.com/file.pdf"
        assert model.page_start == -1  # DOCUMENT_PAGE_UNLIMITED
        assert model.page_end == -1

    def test_ocrllm_with_pages(self):
        """Test OCRLLM with page range."""
        model = OCRLLM(
            file_url="https://example.com/file.pdf",
            page_start=1,
            page_end=5
        )

        assert model.file_url == "https://example.com/file.pdf"
        assert model.page_start == 1
        assert model.page_end == 5

    def test_ocrllm_validation(self):
        """Test OCRLLM validation."""
        with pytest.raises(ValidationError):
            OCRLLM()  # Missing required file_url


class TestImageGenerate:
    """Test cases for ImageGenerate model."""

    def test_image_generate_basic(self):
        """Test basic ImageGenerate creation."""
        model = ImageGenerate(prompt="A beautiful sunset")

        assert model.prompt == "A beautiful sunset"
        assert model.width == 1024
        assert model.height == 1024

    def test_image_generate_custom_size(self):
        """Test ImageGenerate with custom size."""
        model = ImageGenerate(
            prompt="A cat",
            width=512,
            height=768
        )

        assert model.prompt == "A cat"
        assert model.width == 512
        assert model.height == 768

    def test_image_generate_validation(self):
        """Test ImageGenerate validation."""
        with pytest.raises(ValidationError):
            ImageGenerate()  # Missing required prompt


class TestTTSInput:
    """Test cases for TTSInput model."""

    def test_tts_input_basic(self):
        """Test basic TTSInput creation."""
        model = TTSInput(text="Hello world", vcn="xiaoyan")

        assert model.text == "Hello world"
        assert model.vcn == "xiaoyan"
        assert model.speed == 50

    def test_tts_input_custom_speed(self):
        """Test TTSInput with custom speed."""
        model = TTSInput(text="Test", vcn="xiaofeng", speed=75)

        assert model.text == "Test"
        assert model.vcn == "xiaofeng"
        assert model.speed == 75

    def test_tts_input_validation(self):
        """Test TTSInput validation."""
        with pytest.raises(ValidationError):
            TTSInput(text="Hello")  # Missing required vcn


class TestSmartTTSInput:
    """Test cases for SmartTTSInput model."""

    def test_smart_tts_input_basic(self):
        """Test basic SmartTTSInput creation."""
        model = SmartTTSInput(text="Hello", vcn="smart_voice")

        assert model.text == "Hello"
        assert model.vcn == "smart_voice"
        assert model.speed == 50

    def test_smart_tts_input_custom_speed(self):
        """Test SmartTTSInput with custom speed."""
        model = SmartTTSInput(text="Test", vcn="voice", speed=80)

        assert model.text == "Test"
        assert model.vcn == "voice"
        assert model.speed == 80


class TestImageUnderstandingInput:
    """Test cases for ImageUnderstandingInput model."""

    def test_image_understanding_basic(self):
        """Test basic ImageUnderstandingInput creation."""
        model = ImageUnderstandingInput(
            question="What's in this image?",
            image_url="https://example.com/image.jpg"
        )

        assert model.question == "What's in this image?"
        assert model.image_url == "https://example.com/image.jpg"

    def test_image_understanding_validation(self):
        """Test ImageUnderstandingInput validation."""
        with pytest.raises(ValidationError):
            ImageUnderstandingInput(question="Test")  # Missing image_url


class TestValidateEnglish:
    """Test cases for validate_english function."""

    def test_validate_english_valid(self):
        """Test validate_english with valid input."""
        result = validate_english("hello world 123")
        assert result == "hello world 123"

    def test_validate_english_alphanumeric(self):
        """Test validate_english with alphanumeric input."""
        result = validate_english("test123 ABC xyz")
        assert result == "test123 ABC xyz"

    def test_validate_english_empty(self):
        """Test validate_english with empty string."""
        result = validate_english("")
        assert result == ""

    def test_validate_english_chinese(self):
        """Test validate_english with Chinese characters."""
        with pytest.raises(HTTPException) as exc_info:
            validate_english("测试 test")

        assert exc_info.value.status_code == 422
        assert "search_query参数不支持中文检索" in str(exc_info.value.detail)

    def test_validate_english_special_chars(self):
        """Test validate_english with special characters."""
        with pytest.raises(HTTPException):
            validate_english("test@#$%")


class TestArXivInput:
    """Test cases for ArXivInput model."""

    def test_arxiv_input_valid(self):
        """Test ArXivInput with valid English query."""
        model = ArXivInput(search_query="machine learning")
        assert model.search_query == "machine learning"

    def test_arxiv_input_alphanumeric(self):
        """Test ArXivInput with alphanumeric query."""
        model = ArXivInput(search_query="AI 2023 research")
        assert model.search_query == "AI 2023 research"

    def test_arxiv_input_chinese(self):
        """Test ArXivInput with Chinese characters."""
        with pytest.raises(HTTPException):
            ArXivInput(search_query="机器学习")

    def test_arxiv_input_validation(self):
        """Test ArXivInput validation."""
        with pytest.raises(ValidationError):
            ArXivInput()  # Missing required search_query


class TestTTIInput:
    """Test cases for TTIInput model."""

    def test_tti_input_basic(self):
        """Test basic TTIInput creation."""
        model = TTIInput(description="A beautiful landscape")
        assert model.description == "A beautiful landscape"

    def test_tti_input_validation(self):
        """Test TTIInput validation."""
        with pytest.raises(ValidationError):
            TTIInput()  # Missing required description


class TestISEInput:
    """Test cases for ISEInput model."""

    def test_ise_input_basic(self):
        """Test basic ISEInput creation."""
        # Create valid base64 audio data
        audio_data = base64.b64encode(b"fake audio data").decode()

        model = ISEInput(audio_data=audio_data)

        assert model.audio_data == audio_data
        assert model.text == ""
        assert model.language == "cn"
        assert model.category == "read_sentence"
        assert model.group == "adult"

    def test_ise_input_full_params(self):
        """Test ISEInput with all parameters."""
        audio_data = base64.b64encode(b"fake audio").decode()

        model = ISEInput(
            audio_data=audio_data,
            text="hello world",
            language="en",
            category="read_word",
            group="youth"
        )

        assert model.audio_data == audio_data
        assert model.text == "hello world"
        assert model.language == "en"
        assert model.category == "read_word"
        assert model.group == "youth"

    def test_ise_input_invalid_group(self):
        """Test ISEInput with invalid group."""
        audio_data = base64.b64encode(b"fake audio").decode()

        with pytest.raises(ValidationError) as exc_info:
            ISEInput(audio_data=audio_data, group="invalid")

        assert "Invalid group" in str(exc_info.value)

    def test_ise_input_empty_audio_data(self):
        """Test ISEInput with empty audio data."""
        with pytest.raises(ValidationError) as exc_info:
            ISEInput(audio_data="")

        assert "audio_data cannot be empty" in str(exc_info.value)

    def test_ise_input_invalid_base64(self):
        """Test ISEInput with invalid base64 audio data."""
        with pytest.raises(ValidationError) as exc_info:
            ISEInput(audio_data="invalid_base64!")

        assert "must be valid base64 encoded string" in str(exc_info.value)

    def test_ise_input_valid_groups(self):
        """Test ISEInput with all valid groups."""
        audio_data = base64.b64encode(b"fake audio").decode()

        for group in ["pupil", "youth", "adult"]:
            model = ISEInput(audio_data=audio_data, group=group)
            assert model.group == group

    def test_ise_input_validation_missing_audio(self):
        """Test ISEInput validation when audio_data is missing."""
        with pytest.raises(ValidationError):
            ISEInput()  # Missing required audio_data