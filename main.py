"""Run a simple terminal demo of the PawPal+ logic layer."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


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


if __name__ == "__main__":
    main()
