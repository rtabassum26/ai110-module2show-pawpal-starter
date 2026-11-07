"""Core classes for the PawPal+ logic layer."""

from dataclasses import asdict, dataclass, field, replace
import json
from pathlib import Path
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


    def save_to_json(self, path: str | Path = "data.json") -> None:
        """Save owner, pets, and tasks as JSON using ISO date strings."""
        data = {"name": self.name, "pets": []}
        for pet in self.pets:
            tasks = []
            for task in pet.tasks:
                record = asdict(task)
                record["due_date"] = task.due_date.isoformat()
                tasks.append(record)
            data["pets"].append({"name": pet.name, "species": pet.species, "tasks": tasks})
        destination = Path(path)
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        temporary.write_text(json.dumps(data, indent=2), encoding="utf-8")
        temporary.replace(destination)

    @classmethod
    def load_from_json(cls, path: str | Path = "data.json") -> "Owner":
        """Restore an owner and nested objects, rejecting malformed data."""
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            if not isinstance(data["name"], str) or not isinstance(data["pets"], list):
                raise ValueError("Invalid owner fields.")
            owner = cls(data["name"])
            for record in data["pets"]:
                if not isinstance(record["name"], str) or not isinstance(record["species"], str):
                    raise ValueError("Invalid pet fields.")
                if not isinstance(record["tasks"], list):
                    raise ValueError("Invalid task list.")
                pet = Pet(record["name"], record["species"])
                for saved in record["tasks"]:
                    fields = dict(saved)
                    fields["due_date"] = date.fromisoformat(fields["due_date"])
                    if type(fields["completed"]) is not bool:
                        raise ValueError("Invalid completion status.")
                    if type(fields["duration_minutes"]) is not int:
                        raise ValueError("Invalid duration.")
                    if not all(isinstance(fields[key], str) for key in
                               ("description", "time", "priority", "frequency")):
                        raise ValueError("Invalid task text fields.")
                    pet.add_task(Task(**fields))
                owner.add_pet(pet)
            return owner
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            raise ValueError("Cannot load data: invalid PawPal JSON file.") from exc


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
        """Complete a task once and schedule daily/weekly recurrence from today."""
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
                due_date=date.today() + timedelta(days=intervals[task.frequency]),
                completed=False,
            )
            pet.add_task(next_task)


    def next_available_slot(
        self, day: date, duration_minutes: int,
        start_time: str = "08:00", end_time: str = "20:00",
    ) -> str | None:
        """Find the earliest duration-sized gap across all pets in a day window."""
        if duration_minutes <= 0:
            raise ValueError("Duration must be positive.")
        start = datetime.combine(day, datetime.strptime(start_time, "%H:%M").time())
        end = datetime.combine(day, datetime.strptime(end_time, "%H:%M").time())
        if end <= start:
            raise ValueError("End time must be later than start time.")
        length = timedelta(minutes=duration_minutes)
        intervals = []
        for task in self.owner.get_all_tasks():
            if task.completed:
                continue
            task_start = datetime.combine(task.due_date, datetime.strptime(task.time, "%H:%M").time())
            task_end = task_start + timedelta(minutes=task.duration_minutes)
            if task_start < end and task_end > start:
                intervals.append((task_start, task_end))
        candidate = start
        for busy_start, busy_end in sorted(intervals):
            if candidate + length <= busy_start:
                return candidate.strftime("%H:%M")
            candidate = max(candidate, busy_end)
        if candidate + length <= end:
            return candidate.strftime("%H:%M")
        return None
