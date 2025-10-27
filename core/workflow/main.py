"""
Spark Flow Main Application Module

This module serves as the entry point for the Spark Flow workflow engine application.
It initializes the FastAPI application with all necessary middleware, routers, and
extensions including metrics, tracing, and graceful shutdown handling.
"""

import json
import multiprocessing
import os
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from workflow.api.v1.router import old_auth_router, sparkflow_router, workflow_router
from workflow.cache.event_registry import EventRegistry
from workflow.extensions.fastapi.handler.validation import validation_exception_handler
from workflow.extensions.fastapi.middleware.auth import AuthMiddleware
from workflow.extensions.fastapi.middleware.otlp import OtlpMiddleware
from workflow.extensions.graceful_shutdown.graceful_shutdown import GracefulShutdown
from workflow.extensions.middleware.initialize import initialize_services


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.

    This function initializes the FastAPI app with all necessary middleware,
    routers, exception handlers, and lifecycle event handlers. It sets up
    CORS, graceful shutdown, and route logging functionality.

    :return: Configured FastAPI application instance
    """
    # Initialize application services and middleware
    initialize_services()

    # Create the FastAPI application instance
    app = FastAPI()

    # Configure CORS middleware to allow cross-origin requests
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,  # type: ignore[arg-type]
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(OtlpMiddleware)  # type: ignore[arg-type]
    app.add_middleware(AuthMiddleware)  # type: ignore[arg-type]

    # Include API routers for different endpoints
    app.include_router(sparkflow_router)
    app.include_router(workflow_router)
    app.include_router(old_auth_router)

    # Add global exception handler for request validation errors
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,  # type: ignore[arg-type]
    )

    # Configure graceful shutdown handler
    shutdown_handler = GracefulShutdown(
        event=EventRegistry(),
        check_interval=int(os.getenv("SHUTDOWN_INTERVAL", "2")),
        timeout=int(os.getenv("SHUTDOWN_TIMEOUT", "180")),
    )

    # Register startup event handler to log all available routes
    @app.on_event("startup")
    async def print_routes() -> None:
        """
        Log all registered routes during application startup.

        This function collects information about all registered routes
        and logs them in JSON format for debugging and monitoring purposes.
        """
        route_infos = []
        for route in app.routes:
            if isinstance(route, APIRoute):
                route_infos.append(
                    {
                        "path": route.path,
                        "name": route.name,
                        "methods": list(route.methods),
                    }
                )
            else:
                route_infos.append(
                    {
                        "path": getattr(route, "path", "unknown"),
                        "name": getattr(route, "name", "unknown"),
                        "methods": "N/A",
                    }
                )
        logger.info("Registered routes:")
        for route_info in route_infos:
            logger.info(json.dumps(route_info, ensure_ascii=False))
        logger.info("🚀 FastAPI service started successfully!")
        print("🚀 FastAPI service started successfully!")

    # Define final shutdown logic callback
    async def do_final_shutdown_logic() -> None:
        """
        Execute final cleanup logic during application shutdown.

        This function is called as part of the graceful shutdown process
        to perform any necessary cleanup operations.
        """
        print("🧹 Final shutdown hook executed.")

    # Register shutdown event handler for graceful shutdown
    @app.on_event("shutdown")
    async def shutdown() -> None:
        """
        Handle application shutdown gracefully.

        This function ensures that the application shuts down cleanly
        by running the graceful shutdown handler with the final cleanup callback.
        """
        await shutdown_handler.run(shutdown_callback=do_final_shutdown_logic)

    return app


def _get_worker_count() -> int:
    """
    Get the number of workers to use for the application.
    """
    worker_count: int = int(os.getenv("WORKERS", "0"))
    if worker_count == 0:
        worker_count = multiprocessing.cpu_count() + 1
    logger.debug(f"🔍 Worker count: {worker_count}")
    return worker_count


if __name__ == "__main__":
    # Main entry point for the Spark Flow application.
    # This block initializes the application environment and starts the Uvicorn
    # ASGI server with appropriate configuration for different platforms.

    # Log the current platform for debugging purposes
    logger.debug(f"🔍 Current platform: {sys.platform}")

    # Start the Uvicorn ASGI server with platform-specific configuration
    uvicorn.run(
        app="main:create_app",  # Reference to the FastAPI app factory function
        host="0.0.0.0",  # Bind to all available network interfaces
        port=int(os.getenv("SERVICE_PORT", "7880")),  # Default port 7880
        workers=_get_worker_count(),
        reload=(
            os.getenv("RELOAD", "false").lower() == "true"
        ),  # Enable auto-reload for development
        log_level=os.getenv(
            "LOG_LEVEL", "error"
        ).lower(),  # Set log level to error to reduce noise
        ws_ping_interval=None,  # Disable WebSocket ping interval
        ws_ping_timeout=None,  # Disable WebSocket ping timeout
    )
