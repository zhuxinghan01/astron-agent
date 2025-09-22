"""
Spark Link Server Main Entry Point

This module serves as the main entry point for the Spark Link server application.
It initializes the necessary environment variables for Polaris configuration
and starts the SparkLinkServer instance.
"""

from app.start_server import SparkLinkServer

if __name__ == "__main__":
    SparkLinkServer().start()
