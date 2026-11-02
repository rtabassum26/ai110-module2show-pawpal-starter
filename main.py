"""Run a simple terminal demo of the PawPal+ logic layer."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def print_tasks(title: str, tasks: list[Task]) -> None:
    """Print a readable list of tasks for a sorting or filtering demo."""
    print(f"\n{title}")
    if not tasks:
        print("No matching tasks.")
    for task in tasks:
        status = "Complete" if task.completed else "Pending"
        print(f"{task.time} | {task.description} | {status}")


def main() -> None:
    """Create two pets and display their daily care plan."""
    today = date.today()
    owner = Owner("Alex")
    dog = Pet("Biscuit", "dog")
    cat = Pet("Luna", "cat")
    owner.add_pet(dog)
    owner.add_pet(cat)

    dog.add_task(Task("Morning walk", today, "09:00", 30, "high", "daily"))
    cat.add_task(Task("Breakfast", today, "08:00", 10, "high", "daily"))
    cat.add_task(Task("Playtime", today, "18:00", 20, "medium", "daily"))

    # This one-time task lets the status filters show both possible states.
    grooming = Task("Grooming", today, "12:00", 15, "low")
    dog.add_task(grooming)
    grooming.mark_complete()

    scheduler = Scheduler(owner)
    available_minutes = 60
    plan = scheduler.generate_daily_plan(today, available_minutes)

    print("Today's Schedule")
    print(f"Owner: {owner.name} | Available time: {available_minutes} minutes")
    print()
    for task in plan:
        pet_name = next(
            pet.name for pet in owner.pets
            if any(pet_task is task for pet_task in pet.tasks)
        )
        status = "Complete" if task.completed else "Pending"
        print(
            f"{task.time} | {pet_name} | {task.description} | "
            f"{task.duration_minutes} min | Priority: {task.priority} | {status}"
        )
    print()
    print(f"Total planned time: {sum(task.duration_minutes for task in plan)} minutes")


    tasks = owner.get_all_tasks()
    print_tasks("Tasks in insertion order", tasks)
    print_tasks("All tasks sorted by time", scheduler.sort_by_time(tasks))
    print_tasks(
        "Biscuit's tasks sorted by time",
        scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Biscuit")),
    )
    print_tasks(
        "Pending tasks sorted by time",
        scheduler.sort_by_time(scheduler.filter_tasks(completed=False)),
    )
    print_tasks(
        "Completed tasks",
        scheduler.filter_tasks(completed=True),
    )
    print_tasks(
        "Biscuit's pending tasks",
        scheduler.filter_tasks(pet_name="Biscuit", completed=False),
    )


    print("\nRecurring task demo")
    daily_task = dog.tasks[0]
    weekly_task = Task("Weekly brushing", today, "16:00", 15, "low", "weekly")
    cat.add_task(weekly_task)
    for pet, task in [(dog, daily_task), (cat, weekly_task)]:
        scheduler.mark_task_complete(pet, task)
        next_task = pet.tasks[-1]
        print(f"Completed: {task.description} | {task.frequency} | {task.completed}")
        print(f"Next occurrence: {next_task.due_date} at {next_task.time} | Pending")


    print("\nConflict detection demo")
    dog.add_task(Task("Biscuit feeding", today, "19:00", 10, "high"))
    dog.add_task(Task("Biscuit evening walk", today, "19:00", 20, "medium"))
    cat.add_task(Task("Luna feeding", today, "19:00", 10, "high"))
    warnings = scheduler.detect_conflicts(owner.get_all_tasks())
    for warning in warnings:
        print(f"WARNING: {warning}")
    if not warnings:
        print("No scheduling conflicts found.")


if __name__ == "__main__":
    main()
