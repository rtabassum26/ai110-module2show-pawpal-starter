# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Run the terminal demo with `python main.py`. It creates one owner, two pets, and three care tasks, then displays the daily plan in chronological order.

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

The suite contains 14 test cases covering task completion and addition, chronological sorting, pet/status filtering, daily and weekly recurrence, duplicate recurrence prevention, same-time conflicts within and across pets, and daily planning within a priority-based time budget. Edge cases include empty lists, equal times, completed tasks, different dates, one-time tasks, and zero or negative time budgets.

Successful test output from the development environment:

```text
============================= test session starts ==============================
platform linux -- Python 3.12.14, pytest-9.2.0, pluggy-1.7.0
rootdir: /workspace/scratch/609a7b568a6c
plugins: anyio-4.16.0
collected 14 items

tests/test_pawpal.py ..............                                      [100%]

============================== 14 passed in 0.02s ==============================
```

**Confidence Level: ★★★★☆ (4/5).** All 14 tests pass for the covered backend behaviors. This supports confidence in the core scheduling logic, but does not prove every scenario is handled. These tests do not cover Streamlit interactions, duration-overlap detection, or saving data between application runs.

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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
