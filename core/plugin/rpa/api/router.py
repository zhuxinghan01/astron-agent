"""RPA 服务的主路由模块。
本模块定义了 FastAPI 应用的主路由，并设置了一个统一的前缀 `/rpa/v1`。
所有与 RPA 执行相关的路由都在此模块中注册。
"""

from fastapi import APIRouter

from api.v1.execution import execution_router

# 根路由，设置前缀为 /rpa/v1
router = APIRouter(prefix="/rpa/v1")

# 包含执行 RPA 的路由
router.include_router(execution_router)
