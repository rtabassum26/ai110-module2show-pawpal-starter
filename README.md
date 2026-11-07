# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app for organizing care tasks across multiple pets and building daily plans within an available time budget.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

The app separates Python scheduling logic from the Streamlit interface, with Mermaid UML diagrams documenting the class design.

## Features

- Manage multiple pets with a name and species for each pet.
- Add care tasks with a date, time, duration, priority, and once/daily/weekly frequency.
- View tasks in chronological order and filter by pet, completion status, or both.
- Build a daily plan that selects pending tasks by priority within a minute budget, then displays them by time.
- Show warnings for pending tasks with identical dates and start times, including conflicts across pets.
- Complete tasks and automatically create the next daily or weekly occurrence.
- Keep pets and tasks through Streamlit reruns within the active session.
- Run a standalone CLI demo and a 18-case automated backend test suite.

## Getting Started

Use Python 3.10 or newer. From the project root, create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install the starter repository's dependencies and ensure Streamlit and pytest are available:

```bash
python -m pip install -r requirements.txt
python -m pip install streamlit pytest
```

Launch the browser interface:

```bash
python -m streamlit run app.py
```

Run the terminal demo:

```bash
python main.py
```

## Project Files

| File | Purpose |
|------|---------|
| `pawpal_system.py` | Owner, Pet, Task, and Scheduler backend classes. |
| `app.py` | Streamlit forms, task tables, filters, completion controls, and schedule display. |
| `main.py` | Terminal demonstration of the backend behaviors. |
| `tests/test_pawpal.py` | Automated backend tests. |
| `diagrams/uml_draft.mmd` | Initial class design. |
| `diagrams/uml_final.mmd` | Class diagram matching the final backend. |
| `reflection.md` | Design decisions, tradeoffs, and AI collaboration reflection. |

## 🖥️ Sample Output

The opening schedule from `python main.py` is shown below. The full demo also demonstrates filtering, completion, recurrence, and conflict warnings in the Demo Walkthrough.

```text
Today's Schedule
Owner: Alex | Available time: 60 minutes

08:00 | Luna | Breakfast | 10 min | Priority: high | Pending
09:00 | Biscuit | Morning walk | 30 min | Priority: high | Pending
18:00 | Luna | Playtime | 20 min | Priority: medium | Pending

Total planned time: 60 minutes
```

## 🧪 Testing PawPal+

From the project root, run:

```bash
python -m pytest
```

The suite contains 18 test cases, including JSON save/load and duration-aware slot search, covering task completion and addition, chronological sorting, pet/status filtering, daily and weekly recurrence, duplicate recurrence prevention, same-time conflicts within and across pets, and daily planning within a priority-based time budget. Edge cases include empty lists, equal times, completed tasks, different dates, one-time tasks, and zero or negative time budgets.

Successful test output from the development environment:

```text
============================= test session starts ==============================
platform linux -- Python 3.12.14, pytest-9.2.0, pluggy-1.7.0
rootdir: /workspace/scratch/609a7b568a6c
plugins: anyio-4.16.0
collected 18 items

tests/test_pawpal.py ..................                                  [100%]

18 passed, 1 warning in 0.12s

The warning is a deprecation notice from the environment's anyio pytest plugin.
```

**Confidence Level: ★★★★☆ (4/5).** All 18 tests pass for the covered backend behaviors. This supports confidence in the core scheduling logic, but does not prove every scenario is handled. These tests do not cover Streamlit interactions, duration-overlap detection, or every persistence failure scenario.

## 📐 Smarter Scheduling

| Feature | Method(s) | Behavior |
|---------|-----------|----------|
| Time sorting | `Scheduler.sort_by_time()` | Returns a new list ordered by zero-padded `HH:MM` time using `sorted()` and a lambda key; leaves the input list unchanged. |
| Pet/status filtering | `Scheduler.filter_tasks()` | Filters by exact pet name, completion status, or both. `None` leaves that filter unrestricted. |
| Daily planning | `Scheduler.generate_daily_plan()` | Selects pending tasks for the requested date by high, medium, then low priority, with earlier times breaking ties. Skips tasks that exceed the remaining minute budget and returns the selected tasks chronologically. |
| Conflict detection | `Scheduler.detect_conflicts()` | Returns warning strings for pending tasks sharing a due date and start time, within one pet's tasks or across pets. Does not check duration overlaps or automatically resolve conflicts. |
| Recurring tasks | `Scheduler.mark_task_complete()` | Completes the original task and adds a new pending instance to the same pet: daily tasks recur tomorrow, weekly tasks in seven days, calculated from `date.today()` with `timedelta`. One-time tasks do not repeat, and completing the same task again creates no duplicate. |

Use `Scheduler.mark_task_complete(pet, task)` when recurrence is needed. `Task.mark_complete()` only changes the completion status.

Run `python main.py` to see sorting, pet/status filtering, daily and weekly recurrence, and same-time conflict warnings in the terminal.

## 📸 Demo Walkthrough

1. **Add your pets.** Enter an owner name. Under **Add a Pet**, add Biscuit as a dog and Luna as a cat. Each pet appears in the pets table.
2. **Schedule care tasks.** Add a daily Morning walk for Biscuit at 09:00 (30 minutes, high priority), a daily Breakfast for Luna at 08:00 (10 minutes, high priority), and daily Playtime for Luna at 18:00 (20 minutes, medium priority). Use today's date for each task.
3. **Inspect and filter tasks.** Current Tasks displays the entries by date and time, even when they were added out of order. Select a pet and Pending or Complete to narrow the table; All pets and All restore the full view.
4. **Build today's plan.** Select today's date, enter 60 available minutes, and click **Generate schedule**. The plan shows Breakfast, Morning walk, and Playtime in time order, with a summary of three tasks totaling 60 minutes. A smaller budget causes tasks that do not fit to be skipped after priority ordering.
5. **Check a conflict.** Add Biscuit feeding and Luna feeding at 19:00 on the same date. Scheduling Conflicts displays a warning naming the activities and their shared time. The warning remains visible regardless of the task-table filters; it does not automatically reschedule either task.
6. **Complete a recurring task.** Under Complete a Task, select Morning walk and click **Mark complete**. A success message confirms completion and gives the next occurrence's date and time. The original is Complete and a new Pending task is created for tomorrow. Weekly tasks recur seven days from completion day; one-time tasks do not repeat.
7. **Inspect the updated plan.** Completed tasks are excluded from generated plans. To see tomorrow's recurring task, choose tomorrow as the Plan date and click Generate schedule again.

### CLI Demonstration

The terminal demo uses its own sample data, independent of the browser session. Actual output from `python main.py` is shown below; recurrence and conflict dates depend on the day it is run.

```text
Today's Schedule
Owner: Alex | Available time: 60 minutes

08:00 | Luna | Breakfast | 10 min | Priority: high | Pending
09:00 | Biscuit | Morning walk | 30 min | Priority: high | Pending
18:00 | Luna | Playtime | 20 min | Priority: medium | Pending

Total planned time: 60 minutes

Tasks in insertion order
09:00 | Morning walk | Pending
12:00 | Grooming | Complete
08:00 | Breakfast | Pending
18:00 | Playtime | Pending

All tasks sorted by time
08:00 | Breakfast | Pending
09:00 | Morning walk | Pending
12:00 | Grooming | Complete
18:00 | Playtime | Pending

Biscuit's tasks sorted by time
09:00 | Morning walk | Pending
12:00 | Grooming | Complete

Pending tasks sorted by time
08:00 | Breakfast | Pending
09:00 | Morning walk | Pending
18:00 | Playtime | Pending

Completed tasks
12:00 | Grooming | Complete

Biscuit's pending tasks
09:00 | Morning walk | Pending

Recurring task demo
Completed: Morning walk | daily | True
Next occurrence: 2026-11-02 at 09:00 | Pending
Completed: Weekly brushing | weekly | True
Next occurrence: 2026-11-08 at 16:00 | Pending

Conflict detection demo
WARNING: Conflict on 2026-11-01 at 19:00: Biscuit feeding and Biscuit evening walk.
WARNING: Conflict on 2026-11-01 at 19:00: Biscuit feeding and Luna feeding.
```

## Current Limitations

- Persistence uses one local `data.json` file for this app installation; it is not a multi-user database. Click **Save data** after changes.
- Conflict detection checks equal start times, not duration overlaps, and warns rather than resolving conflicts.
- The time budget is a total number of minutes; it does not model available time slots or travel time.
- Task editing is available through the backend's `Task.update_details()` method; the current UI supports adding and completing tasks.
- Daily planning uses dates, task priorities, and a time budget. Additional owner preferences are not implemented.


## Optional Extensions Implemented

### Next Available Slot

`Scheduler.next_available_slot(day, duration_minutes, start_time="08:00", end_time="20:00")` finds the earliest gap that fits a task across all pets. It sorts pending-task intervals and advances past overlapping activities. Unlike the basic exact-time conflict warning, this algorithm considers duration overlaps, including activities extending from the previous day. Completed tasks do not block slots. It returns an `HH:MM` string or `None` when no slot fits; invalid durations or reversed windows raise `ValueError`. The search window stays within one day. Runtime is O(n log n) for n relevant intervals.

In the UI, open **Find Next Available Slot**, choose a date, duration, and start/end window, then click **Find available slot**. The result is a suggestion: enter that time in Schedule a Task to create the task.

### JSON Persistence

`Owner.save_to_json(path="data.json")` saves the owner name, pet names/species, and every task field, including completion and recurrence. It uses custom dictionary conversion with Python's built-in `json` module; dates become ISO strings. `Owner.load_from_json(path="data.json")` reconstructs Owner, Pet, Task, and Python date objects. No serialization dependency is required.

The UI loads `data.json` beside `app.py` when a session starts. If no file exists, it starts with an empty owner. Click **Save data** after adding pets/tasks, changing the owner name, or completing tasks. Restart the app or open a new session to restore the saved state. Unsaved changes are not restored. Invalid files produce an error instead of being silently overwritten. Saving writes a temporary file and then replaces the destination so an interrupted write is less likely to damage the last saved data. Keep data.json local if it contains personal information.

Files changed: `pawpal_system.py` (both algorithms), `app.py` (slot search and save/load), `tests/test_pawpal.py` (extension tests), `diagrams/uml_final.mmd` (new methods), `README.md` (usage), and `ai_interactions.md` (Agent Workflow). Existing CLI behavior remains available through `python main.py`.
