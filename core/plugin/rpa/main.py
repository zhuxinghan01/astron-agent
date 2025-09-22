"""Main entry point for the RPA server application.
This module initializes and starts the RPA server.
"""

from api.app import RPAServer

if __name__ == "__main__":
    RPAServer().start()
