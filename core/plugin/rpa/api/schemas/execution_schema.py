"""RPA 执行请求和响应的 DTO 定义模块。
本模块定义了与 RPA 执行相关的请求和响应数据传输对象（DTO）。
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel


class RPAExecutionRequest(BaseModel):
    """RPA 执行请求的 DTO 定义。"""

    sid: Optional[str] = ""
    project_id: str
    exec_position: Optional[str] = "EXECUTOR"
    params: Optional[Dict[Any, Any]] = None


class RPAExecutionResponse(BaseModel):
    """RPA 执行响应的 DTO 定义。"""

    code: int
    message: str
    sid: Optional[str] = ""
    data: Optional[Dict[Any, Any]] = None
