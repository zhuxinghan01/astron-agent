from pydantic import Field
from pydantic_settings import BaseSettings


class UvicornConfig(BaseSettings):
    UVICORN_APP: str = Field(default="api.app:app")
    UVICORN_HOST: str = Field(default="0.0.0.0")
    UVICORN_PORT: int = Field(default=17870)
    UVICORN_WORKERS: int = Field(default=1)
    UVICORN_RELOAD: bool = Field(default=False)
    UVICORN_WS_PING_INTERVAL: bool = Field(default=False)
    UVICORN_WS_PING_TIMEOUT: bool = Field(default=False)
