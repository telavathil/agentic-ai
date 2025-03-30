"""Base class for all tools."""

from abc import ABC, abstractmethod
from typing import Dict, Any

class Tool(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> Any:
        """Execute the tool with the given parameters"""

    def get_description(self) -> Dict[str, Any]:
        """Get a description of the tool for the agent"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.get_parameters_schema()
        }

    @abstractmethod
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get the schema for the parameters this tool accepts"""
