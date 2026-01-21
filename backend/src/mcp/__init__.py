"""
MCP (Model Context Protocol) package initialization.
Ensures all tools are loaded and registered with the MCP server.
"""

# Import all modules to ensure they get registered with the MCP server
from . import server
from . import tools

# Import and expose the server instance
from .server import mcp_server

__all__ = ["mcp_server"]