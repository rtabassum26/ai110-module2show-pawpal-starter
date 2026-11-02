"""Core classes for the PawPal+ logic layer."""

from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta


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

    def __post_init__(self) -> None:
        """Validate and normalize task scheduling details."""
        self.priority = self.priority.lower()
        self.frequency = self.frequency.lower()
        if self.priority not in {"low", "medium", "high"}:
            raise ValueError("Priority must be low, medium, or high.")
        if self.frequency not in {"once", "daily", "weekly"}:
            raise ValueError("Frequency must be once, daily, or weekly.")
        if self.duration_minutes <= 0:
            raise ValueError("Task duration must be positive.")
        self.time = datetime.strptime(self.time, "%H:%M").strftime("%H:%M")

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
        updated = Task(
            description, due_date, time, duration_minutes,
            priority, frequency, self.completed,
        )
        self.description = updated.description
        self.due_date = updated.due_date
        self.time = updated.time
        self.duration_minutes = updated.duration_minutes
        self.priority = updated.priority
        self.frequency = updated.frequency

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


@dataclass
class Pet:
    """Store a pet's basic information and care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)


class Owner:
    """Manage pets and provide access to their care tasks."""

    def __init__(self, name: str) -> None:
        """Initialize an owner with an empty pet collection."""
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's collection."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return the tasks belonging to all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Organize and manage care tasks for an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        """Connect the scheduler to the owner whose tasks it manages."""
        self.owner = owner

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by their HH:MM scheduled time."""
        return sorted(tasks, key=lambda task: task.time)

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
    ) -> list[Task]:
        """Filter the owner's tasks by pet name and completion status."""
        return [
            task
            for pet in self.owner.pets
            if pet_name is None or pet.name == pet_name
            for task in pet.tasks
            if completed is None or task.completed == completed
        ]

    def generate_daily_plan(
        self, day: date, available_minutes: int
    ) -> list[Task]:
        """Plan the day's tasks within the time budget using priorities."""
        if available_minutes < 0:
            raise ValueError("Available minutes cannot be negative.")
        priorities = {"high": 0, "medium": 1, "low": 2}
        candidates = [
            task for task in self.owner.get_all_tasks()
            if task.due_date == day and not task.completed
        ]
        candidates.sort(key=lambda task: (priorities[task.priority], task.time))
        plan = []
        for task in candidates:
            if task.duration_minutes <= available_minutes:
                plan.append(task)
                available_minutes -= task.duration_minutes
        return self.sort_by_time(plan)

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return warnings for tasks with matching due dates and times."""
        warnings = []
        scheduled = {}
        for task in tasks:
            if task.completed:
                continue
            slot = (task.due_date, task.time)
            if slot in scheduled:
                warnings.append(
                    f"Conflict on {task.due_date} at {task.time}: "
                    f"{scheduled[slot].description} and {task.description}."
                )
            else:
                scheduled[slot] = task
        return warnings

    def mark_task_complete(self, pet: Pet, task: Task) -> None:
        """Complete a task and create its next occurrence if recurring."""
        if not any(owned_pet is pet for owned_pet in self.owner.pets):
            raise ValueError("The pet does not belong to this owner.")
        if not any(pet_task is task for pet_task in pet.tasks):
            raise ValueError("The task does not belong to this pet.")
        if task.completed:
            return
        task.mark_complete()
        intervals = {"daily": 1, "weekly": 7}
        if task.frequency in intervals:
            next_task = replace(
                task,
                due_date=task.due_date + timedelta(days=intervals[task.frequency]),
                completed=False,
            )
            pet.add_task(next_task)
