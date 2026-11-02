# PawPal+ Project Reflection

## 1. System Design
### Three Core User Actions

1. **Enter owner and pet information:** A user should be able to enter their basic information and add the pets they need to care for.

2. **Add and edit care tasks:** A user should be able to add and update tasks such as feeding, walks, and medications, including how long each task takes and its priority.

3. **Generate and view a daily plan:** A user should be able to generate a clear daily care plan based on their available time, task priorities, and preferences.

**a. Initial design**

My initial design includes four classes: Owner, Pet, Task, and Scheduler. An Owner manages a list of pets and provides access to their tasks. Each Pet stores its name, species, and care tasks. A Task represents an activity such as feeding or walking and stores its description, due date, time, duration, priority, frequency, and completion status. It also provides methods for updating its details and marking it complete.

The Scheduler uses the Owner to access tasks across pets. It is responsible for sorting and filtering tasks, generating a daily plan within the available time, detecting scheduling conflicts, and creating the next occurrence when a recurring task is completed. I kept scheduling decisions in this class so that Pet and Task have simpler responsibilities. Task and Pet use Python dataclasses to reduce repetitive setup code.

**b. Design changes**

The four-class structure stayed the same, but some details became clearer during implementation. Task gained a __post_init__() method to validate duration, priority, frequency, and time format. Recurring task completion stays in Scheduler because it needs access to the pet's task list to add the next occurrence. The recurrence calculation was also changed from the original due date to today plus one or seven days to match the exercise instructions. I updated the final UML to include the implemented methods and relationships.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers the requested date, completion status, task priority, and the owner's available minutes. It selects pending tasks for that date, considers high-priority tasks first, and skips tasks that do not fit the remaining budget. It then displays the selected tasks in time order. These constraints keep the daily plan manageable while giving important care tasks priority. Additional owner preferences and specific availability windows are not implemented.

**b. Tradeoffs**

My scheduler checks for tasks with the same due date and start time, but it does not check whether their durations overlap. For example, it warns about two tasks starting at 09:00, but it would miss a 30-minute walk starting at 09:00 that overlaps with feeding at 09:15. This keeps conflict detection simple and easy to understand while meeting the basic requirement. Checking duration overlaps would be a useful improvement for a more complete scheduler.

I reviewed the detect_conflicts() method with AI. One suggestion was to use dictionary.setdefault() to retrieve or store the first task at each time slot in one step. I kept the explicit if/else version because it makes the warning and storage steps easier for me to follow. The current method already scans the tasks once, with average O(n) time and O(n) extra space, so the shorter version would not improve its overall efficiency.

---

## 3. AI Collaboration

**a. How you used AI**

I used ChatGPT to help create the Mermaid UML, generate class skeletons, implement methods, connect Streamlit forms to the backend, and draft tests and documentation. Generating complete files and reviewing the relationships between classes were especially useful. Focused prompts about sorting, recurrence, and test cases made it easier to work through one requirement at a time.

I continued the work in one conversation rather than using separate chat sessions for each phase. Keeping each request focused on a specific step helped me stay organized, although I mixed up the phase order once and corrected it. Separate sessions could have helped keep algorithm planning and testing discussions apart, but I cannot describe that as something I used here.

**b. Judgment and verification**

During the algorithm review, AI suggested using dictionary.setdefault() to shorten conflict detection. The explicit if/else version was kept because it makes the steps easier to understand and already checks tasks in one pass. This review showed me that shorter code does not automatically mean clearer code. I also checked the generated files by running the CLI demo and pytest locally. All tests passed, so I did not need to debug a failing test during this phase.

---

## 4. Testing and Verification

**a. What you tested**

The automated suite has 14 test cases covering task completion and addition, time sorting, pet/status filtering, recurrence, conflict detection, and daily planning. It checks cases such as empty lists, equal times, completed tasks, different dates, repeated completion, and zero or negative budgets. These tests matter because a schedule can look correct in one example while still mishandling a different date or creating duplicate recurring tasks. The CLI demo also shows the main behaviors with readable output.

**b. Confidence**

I would rate my confidence at 4 out of 5 stars. All 14 automated tests passed, which gives me confidence in the backend behaviors they cover. It does not mean every possible case is tested. Next, I would add fixed-date tests for month and year boundaries, more cases with three or more tasks sharing a time, and saved automated tests for Streamlit interactions.

---

## 5. Reflection

**a. What went well**

I am most satisfied with connecting the backend to the UI. Adding a pet or task now creates a real object, and session state keeps that data during interactions. The filters, conflict warnings, and completion messages make the scheduling logic visible instead of leaving it only in the terminal. Building the CLI demo first also made the backend easier to check before connecting the interface.

**b. What you would improve**

I would add a task-editing form so users could correct a time or resolve a conflict directly in the UI. I would also check duration overlaps and save pets and tasks between application runs. For example, the current conflict check misses a walk from 09:00 to 09:30 overlapping with feeding at 09:15. These improvements would make the app more useful without requiring extra classes at this stage.

**c. Key takeaway**

I learned that being the lead architect means staying responsible for the design and checking what the AI produces. AI can generate working code quickly, but I still need to understand where each responsibility belongs, compare the result with the instructions, and verify behavior. In this project, keeping four clear classes, reviewing the recurrence rule, and testing the methods helped keep the work focused. The final code, UML, and documentation also need to agree with each other.
