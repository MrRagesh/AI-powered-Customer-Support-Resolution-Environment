"""Task registry — load and serve task definitions."""
from typing import Dict, Optional, Type
from app.tasks.easy_task import EasyTask
from app.tasks.medium_task import MediumTask
from app.tasks.hard_task import HardTask
from app.core.constants import TASK_IDS, TaskDifficulty


class TaskRegistry:
    def __init__(self):
        self._tasks = {
            TASK_IDS[TaskDifficulty.EASY]:   EasyTask(),
            TASK_IDS[TaskDifficulty.MEDIUM]:  MediumTask(),
            TASK_IDS[TaskDifficulty.HARD]:    HardTask(),
        }

    def get(self, task_id: str):
        return self._tasks.get(task_id)

    def list_all(self) -> list:
        return [
            {
                "task_id":     task_id,
                "difficulty":  t.difficulty,
                "description": t.description,
                "max_steps":   t.max_steps,
            }
            for task_id, t in self._tasks.items()
        ]

    def ids(self) -> list:
        return list(self._tasks.keys())


_registry: Optional[TaskRegistry] = None

def get_task_registry() -> TaskRegistry:
    global _registry
    if _registry is None:
        _registry = TaskRegistry()
    return _registry
