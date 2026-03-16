from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class Tool(ABC):
    """
    Abstract base class for all tools that can be used by the agent.
    Each tool must define its name, description, and input schema.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The identifier for the tool used by the LLM."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A detailed description of what the tool does and when to use it."""
        pass

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """JSON Schema representation of the tool's input arguments."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Executes the tool with the provided arguments."""
        pass

    def to_anthropic_schema(self) -> Dict[str, Any]:
        """Converts the tool definition to Anthropic's tool schema format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters
        }

class ToolRegistry:
    """A registry to manage and execute tools."""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register_tool(self, tool: Tool):
        """Adds a tool to the registry."""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Returns all tool schemas in Anthropic format."""
        return [tool.to_anthropic_schema() for tool in self.tools.values()]

    def execute(self, tool_name: str, **kwargs) -> Any:
        """Finds and executes a tool by name."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found in registry.")
        
        logger.info(f"Executing tool '{tool_name}' with args: {kwargs}")
        return self.tools[tool_name].execute(**kwargs)
