"""Tests for task definitions."""
import pytest
from app.tasks.task_registry import TaskRegistry
from app.core.constants import TASK_IDS, TaskDifficulty


def test_registry_loads_all_tasks():
    registry = TaskRegistry()
    tasks = registry.list_all()
    assert len(tasks) == 3


def test_easy_task_generates_ticket():
    from app.tasks.easy_task import EasyTask
    task = EasyTask()
    ticket = task.generate_ticket()
    assert ticket.text
    assert ticket.category == "refund"


def test_hard_task_generates_uncategorized():
    from app.tasks.hard_task import HardTask
    task = HardTask()
    ticket = task.generate_ticket()
    assert ticket.text
    assert ticket.category is None  # Agent must classify
