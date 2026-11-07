# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked ChatGPT to implement two stretch features in PawPal+: an advanced scheduling algorithm and JSON data persistence. I also asked it to document the changes in the README and AI interactions log.

**What did the agent do?**

The agent implemented a next-available-slot search that considers task durations and overlapping activities across all pets. It also added JSON saving and loading using custom dictionary conversion, including converting dates to strings and restoring them as Python date objects.

The following files were modified or added:

- `pawpal_system.py`: added `Scheduler.next_available_slot()`, `Owner.save_to_json()`, and `Owner.load_from_json()`.
- `app.py`: added slot-search controls, a Save data button, startup loading from `data.json`, and error messages.
- `tests/test_pawpal.py`: added tests for saving and restoring data, malformed files, overlapping tasks, unavailable slots, invalid inputs, and tasks extending from the previous day.
- `diagrams/uml_final.mmd`: added the new backend methods.
- `README.md`: documented the features, persistence workflow, and limitations.
- `ai_interactions.md`: documented the agent workflow.

The agent ran `python -m pytest`; all 18 tests passed. There was one environment plugin deprecation warning. It also used Streamlit's testing tools to check saving data, restoring it in a new session, and finding an available slot. It did not commit or push the changes.

**What did you have to verify or fix manually?**

I noticed that the first AI interactions log did not follow the provided template and asked the agent to correct its headings and structure. I also requested individual updated files instead of a ZIP archive so I could replace the files in my local project. No manual corrections to the stretch-feature code have been reported so far. The remaining manual review is to check the updated UI locally, confirm that saved pets and tasks return after restarting, and verify that suggested slots fit the existing schedule.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Not attempted. -->
