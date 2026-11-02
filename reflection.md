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

No design changes have been made so far. The class skeleton follows the initial UML, and the scheduling methods are still placeholders. I will update this section if implementation or AI feedback leads to a change, explaining what changed and why.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
