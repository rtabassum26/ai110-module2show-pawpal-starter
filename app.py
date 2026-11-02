"""Streamlit interface for the PawPal+ backend."""

from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.write("Add your pets and care tasks, then build a daily plan.")

# Streamlit reruns this script after interactions; retain the same owner object.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner = st.session_state.owner
scheduler = Scheduler(owner)

owner.name = st.text_input("Owner name", value=owner.name)

st.subheader("Add a Pet")
with st.form("add_pet", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    add_pet = st.form_submit_button("Add pet")
if add_pet:
    if not pet_name.strip():
        st.error("Enter a pet name.")
    elif any(pet.name.casefold() == pet_name.strip().casefold() for pet in owner.pets):
        st.error("A pet with that name already exists.")
    else:
        owner.add_pet(Pet(pet_name.strip(), species))
        st.success(f"Added {pet_name.strip()}.")

if owner.pets:
    st.table([{"Pet": pet.name, "Species": pet.species} for pet in owner.pets])
else:
    st.info("Add a pet to start scheduling care tasks.")

st.subheader("Schedule a Task")
if owner.pets:
    with st.form("add_task", clear_on_submit=True):
        selected_pet = st.selectbox("Pet", [pet.name for pet in owner.pets])
        description = st.text_input("Task description")
        due_date = st.date_input("Due date", value=date.today())
        task_time = st.time_input("Time")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
        add_task = st.form_submit_button("Add task")
    if add_task:
        if not description.strip():
            st.error("Enter a task description.")
        else:
            pet = next(pet for pet in owner.pets if pet.name == selected_pet)
            pet.add_task(Task(
                description=description.strip(), due_date=due_date,
                time=task_time.strftime("%H:%M"), duration_minutes=int(duration),
                priority=priority, frequency=frequency,
            ))
            st.success(f"Added task for {pet.name}.")


def task_rows(tasks: list[Task]) -> list[dict]:
    """Convert backend task objects into readable table rows."""
    return [
        {
            "Pet": next(pet.name for pet in owner.pets if any(item is task for item in pet.tasks)),
            "Task": task.description, "Date": str(task.due_date), "Time": task.time,
            "Minutes": task.duration_minutes, "Priority": task.priority,
            "Frequency": task.frequency, "Status": "Complete" if task.completed else "Pending",
        }
        for task in tasks
    ]


st.subheader("Complete a Task")
pending = scheduler.sort_by_time(scheduler.filter_tasks(completed=False))
if pending:
    def completion_label(index: int) -> str:
        """Identify a pending task by pet, activity, date, and time."""
        row = task_rows([pending[index]])[0]
        return f"{row['Pet']} — {row['Task']} — {row['Date']} {row['Time']}"

    with st.form("complete_task"):
        selected_index = st.selectbox(
            "Task to complete", range(len(pending)), format_func=completion_label,
        )
        complete = st.form_submit_button("Mark complete")
    if complete:
        task = pending[selected_index]
        pet = next(pet for pet in owner.pets if any(item is task for item in pet.tasks))
        scheduler.mark_task_complete(pet, task)
        message = f"Completed {task.description} for {pet.name}."
        if task.frequency in {"daily", "weekly"}:
            next_task = pet.tasks[-1]
            message += f" Next occurrence: {next_task.due_date} at {next_task.time}."
        st.session_state.completion_message = message
        st.rerun()
else:
    st.info("No pending tasks to complete.")
if "completion_message" in st.session_state:
    st.success(st.session_state.pop("completion_message"))

st.subheader("Current Tasks")
pet_options = ["All pets"] + [pet.name for pet in owner.pets]
pet_filter = st.selectbox("Filter by pet", range(len(pet_options)), format_func=lambda i: pet_options[i])
status_filter = st.selectbox("Filter by status", ["All", "Pending", "Complete"])
status = {"All": None, "Pending": False, "Complete": True}[status_filter]
filtered = scheduler.filter_tasks(
    pet_name=None if pet_filter == 0 else pet_options[pet_filter], completed=status,
)
# Order dates first, retaining the Scheduler's time ordering within each date.
visible_tasks = sorted(scheduler.sort_by_time(filtered), key=lambda task: task.due_date)
if visible_tasks:
    st.table(task_rows(visible_tasks))
else:
    st.info("No tasks match these filters.")

st.subheader("Scheduling Conflicts")
st.caption("Checks pending tasks across all pets, regardless of the table filters. Only identical dates and start times are checked.")
conflicts = scheduler.detect_conflicts(owner.get_all_tasks())
if conflicts:
    for warning in conflicts:
        st.warning(warning)
    st.info("Review the pet names and times in Current Tasks and arrange different start times before following the schedule.")
else:
    st.success("No same-time conflicts among pending tasks.")

st.subheader("Build Schedule")
plan_day = st.date_input("Plan date", value=date.today())
available_minutes = st.number_input("Available time (minutes)", min_value=0, value=60)
# Retain the user's request and recompute from current backend data on each rerun.
if st.button("Generate schedule"):
    st.session_state.plan_request = (plan_day, int(available_minutes))
if "plan_request" in st.session_state:
    requested_day, budget = st.session_state.plan_request
    st.write(f"Daily plan for {requested_day} ({budget} minutes available)")
    plan = scheduler.generate_daily_plan(requested_day, budget)
    if plan:
        st.table(task_rows(plan))
        st.success(f"Planned {len(plan)} tasks totaling {sum(task.duration_minutes for task in plan)} minutes.")
        st.caption("Pending tasks are selected by priority within your time budget, then shown by time.")
        for warning in scheduler.detect_conflicts(plan):
            st.warning(warning)
    else:
        st.info("No pending tasks fit this date and time budget.")
