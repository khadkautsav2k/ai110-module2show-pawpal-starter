# PawPal+ Project Reflection

## 1. System Design
 Three core actions: add a pet, see today's tasks, food to feed

**a. Initial design**

- Briefly describe your initial UML design.
Firstly, I created four important attributes for Pawpal. 
- What classes did you include, and what responsibilities did you assign to each?
I assign adding a pet option to add a new pet on the system, every time timely care for the pets, pet food to serve everyday, todays task if there's any. 

**b. Design changes**

- Did your design change during implementation?
yes
- If yes, describe at least one change and why you made it.
Back-references: TimelyCare now holds direct task and pet objects (not just IDs).
Filter methods: Pet.get_pending_tasks() and Pet.get_low_stock_foods() for quick queries.
Validation helpers: Task.is_overdue(), TimelyCare.is_overdue(), PetFood.needs_refill().
Timestamps: Task.completed_at auto-set when complete() is called.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  - **Time constraint**: Tasks have scheduled_at timestamps; scheduler warns if tasks are overdue
  - **Priority constraint**: Tasks have priority levels (high/medium/low); Owner.get_all_pending_by_priority() surfaces high-priority tasks first
  - **Duration constraint**: Tasks have duration_minutes; used to detect overlapping schedule conflicts
  - **Frequency constraint**: Recurring tasks (daily/weekly) auto-generate next occurrence when marked complete
  - **Completion status**: Scheduler filters tasks by completed boolean flag to distinguish pending vs finished work

- How did you decide which constraints mattered most?
  - **Time is primary**: Without scheduled_at, the entire scheduling system collapses. Overdue detection is critical for owner awareness
  - **Priority is secondary**: If everything is due now, we need to triage by importance (high → medium → low)
  - **Duration and conflict detection are tertiary**: Most useful once tasks are already prioritized, prevents scheduling accidents
  - **Frequency is optional but valuable**: Makes recurring care tasks (feeding, medication) manageable without manual re-entry

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

  **Tradeoff: Exact interval overlap detection vs. buffer-aware scheduling**
  
  The conflict detection algorithm uses exact interval math: `task1.start < task2.end AND task2.start < task1.end`. This correctly identifies any task overlap by even 1 minute.
  
  **Alternative approach not implemented**: Add a `buffer_minutes` field to warn owners when tasks are close (e.g., within 5 minutes). This would require O(n²) comparisons with range widening, adding complexity.
  
  **Why this tradeoff is reasonable**:
  - For a pet care app, exactly detecting conflicts is more important than fuzzy buffers
  - The current approach is Pythonic and O(n²) is acceptable—most pets have < 20 tasks per day
  - If many tasks have zero duration_minutes (default), they're filtered out automatically, reducing actual conflict pairs to check
  - Future enhancement: Once owners report "tasks feel too tight," we can add buffer_minutes as opt-in scheduling slack

- Why is that tradeoff reasonable for this scenario?
  - Pet care tasks are typically spaced far apart (feeding at 8am, walk at noon, medication at 6pm)
  - Over-detection (exact overlaps) is safer than under-detection (missing real conflicts)
  - The algorithm is transparent and simple—easy for owners to understand why conflicts are flagged

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
  - **Phase 1 (Design)**: Used AI to refine UML class relationships and suggest which methods belonged in each class
  - **Phase 2 (Implementation)**: Used AI to generate pytest test templates and verify dataclass patterns
  - **Phase 3 (UI Integration)**: Used AI to wire Streamlit session_state to backend objects and build button callbacks
  - **Phase 4 (Algorithms)**: Used AI to create comprehensive algorithm analysis docs (PHASE4_ALGORITHM_PLAN.md) ranking sorting, filtering, conflict detection, and recurring task generation by complexity
  - **Phase 5 (Refinement)**: Reviewed AI-generated conflict detection algorithm with fresh eyes to improve clarity and performance
  
- What kinds of prompts or questions were most helpful?
  - Specific algorithm prompts: "Rank these 8 scheduling algorithms by complexity and implementation priority"
  - Code review prompts: "How could this conflict detection be simplified?" (forced algorithm improvement)
  - Test generation prompts: "Write pytest tests for task overdue detection" (fast test skeleton generation)
  - Architecture prompts: "Should recurring task tracking be a parent_id field or a separate Recurrence class?" (helped avoid over-engineering)

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

  **Moment**: During Phase 4 algorithm planning, AI suggested using a sorted+windowing approach for conflict detection (O(n log n) with early exit). While theoretically faster, it required pre-sorting tasks by time and more complex index tracking.
  
  **Decision**: Kept the simple O(n²) brute-force nested loop instead.
  
  **Why**: 
  - Pet task lists are small (typically 5-30 tasks per day), so n² is negligible
  - The nested loop is immediately understandable—anyone reading the code gets the interval overlap logic instantly
  - Premature optimization adds cognitive overhead; we can optimize later if profiling shows this is a bottleneck
  - The current implementation sacrifices O(n log n) performance for O(1) code maintainability
  
- How did you evaluate or verify what the AI suggested?
  - Ran pytest on the original conflict detection to confirm it works on edge cases (zero duration, null times, no conflicts)
  - Compared output on a sample with manually calculated conflicts to verify correctness
  - Measured readability by asking: "Can a new team member understand this in < 30 seconds?"
  - Assessed resource usage: O(n²) * ~20 tasks per day = 400 comparisons—negligible on modern hardware

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
