"""Module for the agent."""

from typing import Dict, Any, List

from agent.core.client import AnthropicClient
from agent.core.state import AgentState, TaskStatus
from agent.planning.planner import TaskPlanner
from agent.execution.executor import StepExecutor
from tools.calculator import Calculator
from config.settings import settings

class Agent:
    """Class for the agent."""

    def __init__(self):
        """Initialize the agent."""
        self.state = AgentState()
        self.planner = TaskPlanner()
        self.executor = StepExecutor()
        self.client = AnthropicClient(model=settings.anthropic_model)

        # Initialize tools
        self.tools_registry = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """Register default tools"""
        calculator = Calculator()
        self.tools_registry[calculator.name] = calculator

    def register_tool(self, tool):
        """Register a new tool"""
        self.tools_registry[tool.name] = tool

    async def process_task(self, task_description: str) -> Dict[str, Any]:
        """Process a task from start to finish"""
        # Create a new task
        task_id = self.state.create_task(task_description)
        self.state.update_task(task_id, status=TaskStatus.PLANNING)

        # Step 1: Create a plan
        plan = await self.planner.create_plan(task_description)
        self.state.update_task(task_id, plan=plan, status=TaskStatus.EXECUTING)

        # Step 2: Execute each step in the plan
        results = []
        current_step = 0

        for step in plan:
            current_step += 1
            self.state.update_task(task_id, current_step=current_step)

            # Execute the step
            result = await self.executor.execute_step(step, self.state)

            # Store result in state
            step_id = step["step_id"]
            self.state.tasks[task_id]["results"][step_id] = result

            # Save to memory
            self.state.add_memory(
                f"Step {step_id}: {step['description']}\nResult: {result['output']}",
                memory_type="execution"
            )

            results.append({
                "step": step,
                "result": result
            })

        # Mark task as completed
        self.state.update_task(task_id, status=TaskStatus.COMPLETED)

        # Generate final response
        final_response = await self._generate_final_response(task_id, results)

        return {
            "task_id": task_id,
            "status": "completed",
            "results": results,
            "final_response": final_response
        }

    async def _generate_final_response(self, task_id: str, results: List[Dict[str, Any]]) -> str:
        """Generate a final response summarizing the task execution"""
        task = self.state.get_task(task_id)

        step_summaries = []
        for _idx, result_item in enumerate(results):
            step = result_item["step"]
            result = result_item["result"]

            step_summaries.append(f"Step {step['step_id']}: {step['description']}")
            step_summaries.append(f"Result: {result['output']}")

        all_steps = "\n".join(step_summaries)

        system_prompt = """
        You are an AI assistant tasked with summarizing the results of a completed task.
        Provide a concise but informative summary of what was accomplished, key findings,
        and any important conclusions.
        """

        user_message = f"""
        Task: {task['description']}

        Steps and Results:
        {all_steps}

        Please provide a summary of this completed task.
        """

        response = await self.client.complete_async(
            system_prompt=system_prompt,
            user_message=user_message
        )

        return response
