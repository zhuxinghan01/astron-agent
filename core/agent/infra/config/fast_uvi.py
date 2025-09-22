from pydantic import Field
from pydantic_settings import BaseSettings


class UvicornConfig(BaseSettings):
    uvicorn_app: str = Field(default="api.app:app")
    uvicorn_host: str = Field(default="0.0.0.0")
    uvicorn_port: int = Field(default=17870)
    uvicorn_workers: int = Field(default=1)
    uvicorn_reload: bool = Field(default=False)
    uvicorn_ws_ping_interval: bool = Field(default=False)
    uvicorn_ws_ping_timeout: bool = Field(default=False)
