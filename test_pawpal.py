"""Quick tests for the PawPal+ core classes."""

from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_task_status():
    """Completing a pending task should change its status to complete."""
    task = Task("Morning walk", date(2026, 11, 1), "09:00", 30, "high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task should increase the pet's task count by one."""
    pet = Pet("Biscuit", "dog")
    task = Task("Breakfast", date(2026, 11, 1), "08:00", 10, "high")
    initial_count = len(pet.tasks)

    pet.add_task(task)

    assert len(pet.tasks) == initial_count + 1
    assert pet.tasks[-1] is task


@pytest.mark.parametrize("frequency,days", [("daily", 1), ("weekly", 7)])
def test_recurring_completion_creates_next_occurrence(frequency, days):
    """Completing an overdue recurring task schedules from today only once."""
    owner = Owner("Alex")
    pet = Pet("Biscuit", "dog")
    owner.add_pet(pet)
    task = Task("Care", date.today() - timedelta(days=3), "09:00", 10, "high", frequency)
    pet.add_task(task)
    scheduler = Scheduler(owner)

    scheduler.mark_task_complete(pet, task)

    assert task.completed is True
    assert len(pet.tasks) == 2
    following = pet.tasks[-1]
    assert following is not task
    assert following.due_date == date.today() + timedelta(days=days)
    assert following.completed is False
    assert (following.description, following.time, following.duration_minutes,
            following.priority, following.frequency) == (
                task.description, task.time, task.duration_minutes,
                task.priority, task.frequency)
    scheduler.mark_task_complete(pet, task)
    assert len(pet.tasks) == 2


def test_one_time_completion_does_not_repeat():
    """A one-time task should not create a new occurrence."""
    owner = Owner("Alex")
    pet = Pet("Biscuit", "dog")
    owner.add_pet(pet)
    task = Task("Checkup", date.today(), "10:00", 30, "high")
    pet.add_task(task)

    Scheduler(owner).mark_task_complete(pet, task)

    assert task.completed is True
    assert len(pet.tasks) == 1


@pytest.mark.parametrize("same_pet", [True, False])
def test_conflicts_detected_within_and_across_pets(same_pet):
    """Same-date, same-time tasks produce a warning regardless of pet."""
    owner = Owner("Alex")
    dog, cat = Pet("Biscuit", "dog"), Pet("Luna", "cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    first = Task("Feeding", date.today(), "19:00", 10, "high")
    second = Task("Walk", date.today(), "19:00", 20, "medium")
    dog.add_task(first)
    (dog if same_pet else cat).add_task(second)

    warnings = Scheduler(owner).detect_conflicts(owner.get_all_tasks())

    assert len(warnings) == 1
    assert "19:00" in warnings[0]
    assert "Feeding" in warnings[0] and "Walk" in warnings[0]
    assert not first.completed and not second.completed


def test_conflicts_ignore_other_dates_times_and_completed_tasks():
    """Distinct slots and completed tasks should not raise warnings."""
    tasks = [
        Task("Feed", date.today(), "08:00", 10, "high"),
        Task("Walk", date.today(), "09:00", 20, "high"),
        Task("Tomorrow", date.today() + timedelta(days=1), "08:00", 10, "high"),
        Task("Finished", date.today(), "08:00", 10, "high", completed=True),
    ]
    scheduler = Scheduler(Owner("Alex"))
    assert scheduler.detect_conflicts(tasks) == []
    assert scheduler.detect_conflicts([]) == []
