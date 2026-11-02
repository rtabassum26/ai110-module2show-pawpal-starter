"""Class skeletons for the PawPal+ logic layer."""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Task:
    """Represent a pet care activity and its scheduling details."""

    description: str
    due_date: date
    time: str
    duration_minutes: int
    priority: str
    frequency: str = "once"
    completed: bool = False

    def update_details(
        self,
        description: str,
        due_date: date,
        time: str,
        duration_minutes: int,
        priority: str,
        frequency: str,
    ) -> None:
        """Update the task's description and scheduling details."""
        pass

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        pass


@dataclass
class Pet:
    """Store a pet's basic information and care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        pass


class Owner:
    """Manage pets and provide access to their care tasks."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's collection."""
        pass

    def get_all_tasks(self) -> list[Task]:
        """Return the tasks belonging to all of this owner's pets."""
        pass


class Scheduler:
    """Organize and manage care tasks for an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by their HH:MM scheduled time."""
        pass

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
    ) -> list[Task]:
        """Filter the owner's tasks by pet name and completion status."""
        pass

    def generate_daily_plan(
        self, day: date, available_minutes: int
    ) -> list[Task]:
        """Plan the day's tasks within the time budget using priorities."""
        pass

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return warnings for tasks with matching due dates and times."""
        pass

    def mark_task_complete(self, pet: Pet, task: Task) -> None:
        """Complete a task and create its next occurrence if recurring."""
        pass
