"""Module for managing the state of the agent."""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TaskStatus(str, Enum):
    """Enum for the status of a task."""

    PENDING = "PENDING"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class AgentState:
    """Class for managing the state of the agent."""

    def __init__(self):
        """Initialize the agent state."""
        logger.debug("Initializing AgentState")
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.memory: List[Dict[str, Any]] = []
        self.current_task_id: Optional[str] = None

    def create_task(self, description: str) -> str:
        """Create a new task."""
        task_id = str(uuid.uuid4())
        logger.info("Creating new task: %s", description)
        self.tasks[task_id] = {
            "id": task_id,
            "description": description,
            "status": TaskStatus.PENDING,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "plan": [],
            "current_step": 0,
            "results": {},
        }
        self.current_task_id = task_id
        logger.debug("Task created with ID: %s", task_id)
        return task_id

    def update_task(self, task_id: str, **updates) -> None:
        """Update a task."""
        if task_id not in self.tasks:
            logger.error("Task %s not found", task_id)
            raise ValueError(f"Task {task_id} not found")

        logger.debug("Updating task %s with: %s", task_id, updates)
        task = self.tasks[task_id]
        for key, value in updates.items():
            if key in task:
                task[key] = value

        task["updated_at"] = datetime.now().isoformat()
        logger.info("Task %s updated successfully", task_id)

    def add_memory(self, content: str, memory_type: str = "observation") -> None:
        """Add a memory to the agent's memory."""
        logger.debug("Adding memory of type %s", memory_type)
        self.memory.append({
            "content": content,
            "type": memory_type,
            "timestamp": datetime.now().isoformat()
        })
        logger.debug("Memory added. Total memories: %d", len(self.memory))

    def get_recent_memory(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the recent memory of the agent."""
        recent = self.memory[-limit:] if self.memory else []
        logger.debug("Retrieved %d recent memories", len(recent))
        return recent

    def get_task(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a task by id."""
        if task_id is None:
            task_id = self.current_task_id

        if task_id not in self.tasks:
            logger.error("Task %s not found", task_id)
            raise ValueError(f"Task {task_id} not found")

        logger.debug("Retrieved task %s", task_id)
        return self.tasks[task_id]
