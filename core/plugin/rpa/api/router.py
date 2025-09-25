"""Main routing module for RPA service.
This module defines the main routes of the FastAPI application and sets a unified prefix `/rpa/v1`.
All routes related to RPA execution are registered in this module.
"""

from fastapi import APIRouter

from plugin.rpa.api.v1.execution import execution_router

# Root router, set prefix to /rpa/v1
router = APIRouter(prefix="/rpa/v1")

# Include routes for RPA execution
router.include_router(execution_router)
