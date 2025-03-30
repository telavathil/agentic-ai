"""Module for task planning and step generation using LLM-based planning."""

from typing import List, Dict, Any
import json
import logging

from agent.core.client import AnthropicClient
from config.settings import settings

logger = logging.getLogger(__name__)

class TaskPlanner:
    """A planner that breaks down tasks into executable steps using LLM-based planning."""

    def __init__(self, tools_registry: Dict[str, Any] = None):
        logger.debug("Initializing TaskPlanner")
        self.client = AnthropicClient(model=settings.planning_model)
        self.tools_registry = tools_registry or {}

    def _get_tools_description(self) -> str:
        """Generate description of available tools for the system prompt."""
        if not self.tools_registry:
            return "No tools available."

        tools_desc = ["Available tools:"]
        for name, tool in self.tools_registry.items():
            tools_desc.append(f"- {name}: {tool.description}")
            example = tool.get_example()
            if example:
                tools_desc.append(f"  Example: {example}")

        return "\n".join(tools_desc)

    async def create_plan(self, task_description: str, context: str = "") -> List[Dict[str, Any]]:
        """Create a step-by-step plan for completing the task"""
        logger.info("Creating plan for task: %s", task_description)
        if context:
            logger.debug("Additional context: %s", context)

        system_prompt = f"""
        You are an AI task planner. Your job is to break down tasks into clear, executable steps.
        Each step should be specific and actionable.

        {self._get_tools_description()}

        Format your response as a JSON array of steps, where each step has:
        - "step_id": a numeric identifier
        - "description": what needs to be done
        - "requires_tool": boolean indicating if this step needs an external tool
        - "tool_name": the name of the tool if requires_tool is true, otherwise null
        - "tool_parameters": expected parameters for the tool if requires_tool is true, otherwise null

        Make sure the steps are in the correct order and cover all aspects of the task.
        For tool-based steps, use the exact parameter format shown in the examples.
        """

        user_message = f"""
        Task to plan: {task_description}

        Additional context: {context}

        Create a step-by-step plan to complete this task. Return ONLY the JSON array without explanation.
        """

        try:
            logger.debug("Sending request to LLM for plan generation")
            response = await self.client.complete_async(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=settings.planning_temperature,
                max_tokens=settings.max_tokens_response
            )
            logger.debug("Received response from LLM")

            # Parse the response as JSON
            plan = json.loads(response)
            logger.info("Generated plan: %s", json.dumps(plan, indent=2))

            # Validate plan structure
            for step in plan:
                assert "step_id" in step
                assert "description" in step
                assert "requires_tool" in step
                assert "tool_name" in step
                assert "tool_parameters" in step
                logger.debug("Validated step %d: %s", step['step_id'], step['description'])

            return plan

        except (ValueError, SyntaxError, TypeError) as e:
            logger.error("Error creating plan: %s", e, exc_info=True)
            logger.info("Falling back to simple plan")
            # Fallback to a simple plan
            return [
                {
                    "step_id": 1,
                    "description": f"Complete the task: {task_description}",
                    "requires_tool": False,
                    "tool_name": None,
                    "tool_parameters": None
                }
            ]
