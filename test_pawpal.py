"""Quick tests for the PawPal+ core classes."""

from datetime import date

from pawpal_system import Pet, Task


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
