from typing import Any

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, model_validator

from api.schemas.llm_message import LLMMessage


class MetaDataInputs(BaseModel):
    """extra inputs"""

    caller: str = Field(default="chat_open_api")
    caller_sid: str = Field(default="")


class BaseInputs(BaseModel):
    uid: str = Field(default="", description="uid", max_length=64)
    messages: list[LLMMessage]
    stream: bool = Field(default=False)
    meta_data: MetaDataInputs = Field(default_factory=MetaDataInputs)

    @model_validator(mode="before")
    @classmethod
    def validate_messages_params(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values
        messages = values.get("messages", [])
        if isinstance(messages, list) and not messages:
            values.pop("messages", None)
            return values

        next_role = "user"
        for i, message in enumerate(messages):
            if not isinstance(message, dict):
                return values

            if not message.get("content"):
                # Content cannot be empty
                raise RequestValidationError(
                    errors=[
                        {
                            "type": "literal_error",
                            "loc": ("body", "messages", i, "content"),
                            "msg": "'content' cannot be empty",
                        }
                    ]
                )

            if message.get("role") == "system":
                # System role not supported
                raise RequestValidationError(
                    errors=[
                        {
                            "type": "literal_error",
                            "loc": ("body", "messages", i, "role"),
                            "msg": "'role' must be user or assistant",
                        }
                    ]
                )

            if message.get("role") != next_role:
                # Wrong order
                raise RequestValidationError(
                    errors=[
                        {
                            "type": "literal_error",
                            "loc": ("body", "messages", i, "role"),
                            "msg": (
                                "messages role order must alternate "
                                "between user and assistant"
                            ),
                        }
                    ]
                )

            next_role = "assistant" if next_role == "user" else "user"

        if next_role != "assistant":
            # Last message is not user
            raise RequestValidationError(
                errors=[
                    {
                        "type": "literal_error",
                        "loc": ("body", "messages"),
                        "msg": "messages must end with user type content",
                    }
                ]
            )

        return values
