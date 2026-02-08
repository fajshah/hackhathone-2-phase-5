from typing import Dict, Any, Callable
from pydantic import BaseModel
import inspect

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class MCPRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.tool_definitions: Dict[str, ToolDefinition] = {}

    def register_tool(self, name: str, description: str, parameters: Dict[str, Any]):
        """
        Decorator to register an MCP tool
        """
        def decorator(func: Callable):
            self.tools[name] = func
            self.tool_definitions[name] = ToolDefinition(
                name=name,
                description=description,
                parameters=parameters
            )
            return func
        return decorator

    def execute_tool(self, name: str, **kwargs) -> Any:
        """
        Execute a registered tool with the given arguments
        """
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
        
        tool_func = self.tools[name]
        return tool_func(**kwargs)

    def get_tool_definition(self, name: str) -> ToolDefinition:
        """
        Get the definition of a registered tool
        """
        if name not in self.tool_definitions:
            raise ValueError(f"Tool definition {name} not found")
        return self.tool_definitions[name]

    def get_all_tool_definitions(self) -> Dict[str, ToolDefinition]:
        """
        Get all registered tool definitions
        """
        return self.tool_definitions

# Global MCP registry instance
mcp_registry = MCPRegistry()