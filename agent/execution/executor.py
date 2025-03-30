"""Module for executing individual steps in a task plan, including tool execution and reasoning."""

from typing import Dict, Any
import logging

from agent.core.client import AnthropicClient
from agent.core.state import AgentState
from config.settings import settings

logger = logging.getLogger(__name__)

class StepExecutor:
    def __init__(self, tools_registry=None):
        logger.debug("Initializing StepExecutor")
        self.client = AnthropicClient(model=settings.anthropic_model)
        self.tools_registry = tools_registry or {}
        logger.debug("Registered %d tools", len(self.tools_registry))

    async def execute_step(self, step: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        """Execute a single step from the plan"""
        logger.info(
            "Executing step %s: %s", step.get('step_id', 'unknown'), step.get('description', ''))

        if step.get("requires_tool", False):
            logger.debug("Step requires tool execution")
            return await self._execute_tool_step(step, state)

        logger.debug("Step requires thinking/reasoning")
        return await self._execute_thinking_step(step, state)

    async def _execute_tool_step(self, step: Dict[str, Any], _state: AgentState) -> Dict[str, Any]:
        """Execute a step that requires an external tool"""
        tool_name = step.get("tool_name")
        tool_parameters = step.get("tool_parameters", {})
        logger.debug("Executing tool %s with parameters: %s", tool_name, tool_parameters)

        if tool_name not in self.tools_registry:
            logger.error("Tool %s not found in registry", tool_name)
            return {
                "status": "error",
                "error": f"Tool {tool_name} not found",
                "output": f"Unable to execute step: Tool {tool_name} is not available."
            }

        try:
            tool = self.tools_registry[tool_name]
            logger.debug("Found tool %s, executing...", tool_name)
            result = await tool.execute(tool_parameters)
            logger.info("Tool %s executed successfully", tool_name)

            return {
                "status": "success",
                "output": result,
                "tool_used": tool_name,
                "tool_parameters": tool_parameters
            }

        except (ValueError, SyntaxError, TypeError) as e:
            logger.error("Error executing tool %s: %s", tool_name, e, exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "output": f"Error executing tool {tool_name}: {str(e)}",
                "tool_used": tool_name,
                "tool_parameters": tool_parameters
            }

    async def _execute_thinking_step(
            self, step: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        """Execute a step that requires thinking/reasoning without using external tools."""
        logger.debug("Starting thinking step execution")

        # Get context from recent memory
        recent_memory = state.get_recent_memory()
        memory_context = "\n".join([f"{mem['type']}: {mem['content']}" for mem in recent_memory])
        logger.debug("Retrieved %d recent memories", len(recent_memory))

        system_prompt = """
        You are an AI assistant executing a specific step in a larger plan.
        Your job is to complete this step by thinking through the problem and providing a solution.
        Be thorough, precise, and focus only on completing the assigned step.
        """

        user_message = f"""
        Step to execute: {step['description']}

        Recent context:
        {memory_context}

        Complete this step by providing your analysis, reasoning, or conclusion.
        """

        logger.debug("Sending request to LLM for thinking step")
        response = await self.client.complete_async(
            system_prompt=system_prompt,
            user_message=user_message,
            temperature=settings.execution_temperature
        )
        logger.info("Thinking step completed successfully")

        return {
            "status": "success",
            "output": response,
            "thinking": response  # Store the thinking process for reflection
        }
