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


def test_sort_by_time_orders_tasks_without_changing_input():
    """Out-of-order times should sort chronologically without mutating input."""
    tasks = [
        Task("Evening", date.today(), "18:00", 10, "low"),
        Task("Morning", date.today(), "8:00", 10, "high"),
        Task("Noon", date.today(), "12:00", 10, "medium"),
    ]
    original = tasks.copy()

    result = Scheduler(Owner("Alex")).sort_by_time(tasks)

    assert [task.time for task in result] == ["08:00", "12:00", "18:00"]
    assert tasks == original
    assert result is not tasks


def test_sort_empty_list_and_equal_times():
    """Empty lists work, and tasks with equal times retain their order."""
    scheduler = Scheduler(Owner("Alex"))
    first = Task("Feed", date.today(), "08:00", 10, "high")
    second = Task("Medicine", date.today(), "08:00", 5, "high")

    assert scheduler.sort_by_time([]) == []
    result = scheduler.sort_by_time([first, second])
    assert result[0] is first
    assert result[1] is second


def test_filter_by_pet_status_and_both():
    """Each filter works independently and can be combined."""
    owner = Owner("Alex")
    dog, cat = Pet("Biscuit", "dog"), Pet("Luna", "cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    walk = Task("Walk", date.today(), "09:00", 20, "high")
    feed = Task("Feed", date.today(), "08:00", 10, "high", completed=True)
    play = Task("Play", date.today(), "18:00", 15, "low")
    dog.add_task(walk)
    dog.add_task(feed)
    cat.add_task(play)
    scheduler = Scheduler(owner)

    assert scheduler.filter_tasks(pet_name="Biscuit") == [walk, feed]
    assert scheduler.filter_tasks(completed=False) == [walk, play]
    assert scheduler.filter_tasks(completed=True) == [feed]
    assert scheduler.filter_tasks("Biscuit", False) == [walk]
    assert scheduler.filter_tasks() == [walk, feed, play]
    assert scheduler.filter_tasks(pet_name="Unknown") == []


def test_pet_with_no_tasks_can_be_filtered():
    """A pet without care tasks should return an empty list."""
    owner = Owner("Alex")
    owner.add_pet(Pet("Biscuit", "dog"))
    assert Scheduler(owner).filter_tasks("Biscuit") == []


def test_daily_plan_prioritizes_and_respects_date_status_and_budget():
    """Only eligible tasks fitting the remaining budget enter the plan."""
    owner = Owner("Alex")
    pet = Pet("Biscuit", "dog")
    owner.add_pet(pet)
    today = date.today()
    tasks = [
        Task("Low priority", today, "07:00", 10, "low"),
        Task("Important", today, "09:00", 20, "high"),
        Task("Too long", today, "10:00", 40, "high"),
        Task("Medium priority", today, "08:00", 10, "medium"),
        Task("Tomorrow", today + timedelta(days=1), "06:00", 5, "high"),
        Task("Finished", today, "06:00", 5, "high", completed=True),
    ]
    for task in tasks:
        pet.add_task(task)

    plan = Scheduler(owner).generate_daily_plan(today, 30)

    assert [task.description for task in plan] == ["Medium priority", "Important"]
    assert sum(task.duration_minutes for task in plan) == 30


def test_daily_plan_handles_empty_zero_and_negative_budget():
    """Empty schedules and zero budgets return no tasks; negative is invalid."""
    owner = Owner("Alex")
    scheduler = Scheduler(owner)
    assert scheduler.generate_daily_plan(date.today(), 60) == []
    pet = Pet("Biscuit", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", date.today(), "09:00", 20, "high"))
    assert scheduler.generate_daily_plan(date.today(), 0) == []
    with pytest.raises(ValueError, match="Available minutes"):
        scheduler.generate_daily_plan(date.today(), -1)


def test_json_round_trip(tmp_path):
    """Saving and loading restores all fields and independent task objects."""
    owner = Owner("Alex")
    pet = Pet("Biscuit", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", date(2026, 12, 31), "09:00", 30, "high", "weekly", True))
    owner.add_pet(Pet("Luna", "cat"))
    path = tmp_path / "data.json"
    owner.save_to_json(path)
    restored = Owner.load_from_json(path)
    assert restored.name == owner.name
    assert restored.pets == owner.pets
    assert restored.pets[0].tasks[0] is not pet.tasks[0]
    assert isinstance(restored.pets[0].tasks[0].due_date, date)
    restored.name = "Updated"
    restored.save_to_json(path)
    assert Owner.load_from_json(path).name == "Updated"


def test_invalid_json_is_rejected(tmp_path):
    path = tmp_path / "data.json"
    path.write_text('{"name": "Alex", "pets": [{}]}')
    with pytest.raises(ValueError, match="invalid PawPal"):
        Owner.load_from_json(path)
    path.write_text('broken json')
    with pytest.raises(ValueError):
        Owner.load_from_json(path)


def test_next_slot_merges_overlaps_across_pets():
    owner = Owner("Alex")
    a, b = Pet("Biscuit", "dog"), Pet("Luna", "cat")
    owner.add_pet(a)
    owner.add_pet(b)
    day = date(2026, 11, 6)
    a.add_task(Task("Walk", day, "08:00", 60, "high"))
    b.add_task(Task("Care", day, "08:30", 60, "high"))
    b.add_task(Task("Done", day, "09:30", 30, "high", completed=True))
    scheduler = Scheduler(owner)
    assert scheduler.next_available_slot(day, 30, "08:00", "10:00") == "09:30"
    assert scheduler.next_available_slot(day, 31, "08:00", "10:00") is None
    assert scheduler.next_available_slot(day + timedelta(days=1), 30) == "08:00"


def test_next_slot_handles_previous_day_and_exact_gap():
    owner = Owner("Alex")
    pet = Pet("Biscuit", "dog")
    owner.add_pet(pet)
    day = date(2026, 11, 6)
    pet.add_task(Task("Late care", day - timedelta(days=1), "23:30", 90, "high"))
    pet.add_task(Task("Early care", day, "01:30", 30, "high"))
    scheduler = Scheduler(owner)
    assert scheduler.next_available_slot(day, 30, "00:00", "02:00") == "01:00"
    with pytest.raises(ValueError):
        scheduler.next_available_slot(day, 0)
    with pytest.raises(ValueError):
        scheduler.next_available_slot(day, 30, "20:00", "08:00")
