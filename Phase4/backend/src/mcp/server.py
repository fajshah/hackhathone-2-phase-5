"""
MCP (Model Context Protocol) server framework for the Todo AI Chatbot.
Provides a framework for creating stateless tools that interact with the database.
"""
from typing import Dict, Any, Callable, Awaitable
from fastapi import HTTPException
from sqlmodel import Session
from ..database import engine
from ..auth import auth_service
from ..models.user import User
import inspect
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServer:
    """
    MCP Server framework that manages tools and their execution.
    Ensures all operations are stateless and properly authenticated.
    """
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        logger.info("MCP Server initialized")

    def register_tool(self, name: str, func: Callable):
        """
        Register a tool with the MCP server.
        """
        self.tools[name] = func
        logger.info(f"Tool '{name}' registered")

    def execute_tool(self, tool_name: str, params: Dict[str, Any], user_token: str) -> Dict[str, Any]:
        """
        Execute a registered tool with the given parameters.
        Handles authentication and database session management.
        """
        # Verify the tool exists
        if tool_name not in self.tools:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

        # Authenticate the user
        user_payload = auth_service.decode_access_token(user_token)
        if not user_payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Extract user info from token
        user_id = user_payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # Create a database session
        with Session(engine) as session:
            # Get the user from the database
            from ..models.user import User
            from sqlmodel import select
            user_stmt = select(User).where(User.id == int(user_id))
            user = session.exec(user_stmt).first()

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Get the tool function
            tool_func = self.tools[tool_name]

            # Check if the function expects a user parameter
            sig = inspect.signature(tool_func)
            if 'user' in sig.parameters:
                # Call the tool function with the user parameter
                result = tool_func(session=session, user=user, **params)
            else:
                # Call the tool function without the user parameter
                result = tool_func(session=session, **params)

        return {
            "success": True,
            "result": result,
            "tool": tool_name
        }

    async def execute_tool_async(self, tool_name: str, params: Dict[str, Any], user_token: str) -> Dict[str, Any]:
        """
        Asynchronously execute a registered tool with the given parameters.
        """
        return self.execute_tool(tool_name, params, user_token)


# Create a global instance of the MCP server
mcp_server = MCPServer()

# Export for use in other modules
__all__ = ["mcp_server", "MCPServer"]

# Helper function to get the current user from the token
def get_current_user_from_token(user_token: str) -> User:
    """
    Helper function to extract user from token.
    """
    user_payload = auth_service.decode_access_token(user_token)
    if not user_payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = user_payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Create a database session
    with Session(engine) as session:
        from ..models.user import User
        from sqlmodel import select
        user_stmt = select(User).where(User.id == int(user_id))
        user = session.exec(user_stmt).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user