from typing import Any, AsyncIterator

from openai import APIError, APITimeoutError, AsyncOpenAI
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from pydantic import BaseModel, ConfigDict

from common_imports import Span
from exceptions.plugin_exc import PluginExc, llm_plugin_error


class BaseLLMModel(BaseModel):
    name: str
    llm: AsyncOpenAI

    model_config = ConfigDict(arbitrary_types_allowed=True)

    async def create_completion(self, messages: list, stream: bool) -> Any:
        return await self.llm.chat.completions.create(
            messages=messages,
            stream=stream,
            model=self.name,
        )

    async def stream(
        self, messages: list, stream: bool, span: Span | None = None
    ) -> AsyncIterator[ChatCompletionChunk]:

        sp = span

        if sp is not None:
            for message in messages:
                sp.add_info_events({message.get("role"): message.get("content")})

            sp.add_info_events({"model": self.name})
            sp.add_info_events({"stream": stream})

        try:

            response = await self.create_completion(messages, stream)
            async for chunk in response:
                chunk_dict = chunk.model_dump()

                if sp is not None:
                    sp.add_info_events({"llm-chunk": chunk.model_dump_json()})

                if chunk_dict.get("code", 0) != 0:
                    llm_plugin_error(chunk_dict.get("code"), chunk_dict.get("message"))

                yield chunk
        except APITimeoutError as e:
            raise PluginExc(-1, "请求服务超时", om=str(e)) from e

        except APIError as error:
            if sp is not None:
                sp.add_info_events({"code": error.code or "null"})
                sp.add_info_events({"message": error.message})
                sp.add_info_events(
                    {"converted-code": str(getattr(error, "code", "unknown"))}
                )
                sp.add_info_events({"converted-message": error.message})
            llm_plugin_error(error.code, error.message)

        except (ValueError, TypeError, KeyError) as e:
            if sp is not None:
                sp.add_info_events({"code": ""})
                sp.add_info_events({"message": str(e)})
                sp.add_info_events({"converted-code": "-1"})
                sp.add_info_events({"converted-message": str(e)})
            llm_plugin_error("-1", str(e))
