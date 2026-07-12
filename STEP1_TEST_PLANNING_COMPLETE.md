# Step 1: Plan What to Test - COMPLETED ✓

## Summary

I've reviewed the PawPal+ system and created a comprehensive test plan for Phase 6. Here's what was documented:

---

## Core Behaviors Identified (21 methods across 5 categories)

### 1. **Sorting Algorithms** (6 methods)
- `Pet.get_tasks_sorted_by_time()` - Chronological ordering
- `Pet.get_tasks_sorted_by_priority()` - Priority + time ordering  
- `Scheduler.get_todays_schedule()` - Today's tasks by time
- `Scheduler.get_todays_schedule_by_priority()` - Today's tasks by priority
- `Owner.get_all_tasks_sorted_by_time()` - All pets chronologically
- `Owner.get_all_tasks_sorted_by_priority()` - All pets by priority

### 2. **Filtering Algorithms** (8+ methods)
- `Pet.get_tasks_by_status(completed)` - Filter by completion
- `Pet.get_high_priority_tasks()` - Filter high-priority only
- `Pet.get_recurring_tasks()` - Filter daily/weekly tasks
- `Pet.get_pending_tasks()` - Filter incomplete tasks
- `Owner.get_all_pending_tasks()` - Pending across all pets
- `Owner.get_all_overdue_tasks()` - Past deadline across pets
- `Owner.get_all_high_priority_tasks()` - High-priority across pets
- `Owner.get_all_pending_by_priority()` - Incomplete by priority

### 3. **Conflict Detection** (2 methods)
- `Scheduler.detect_conflicts_for_pet(pet)` - Find overlapping tasks
- `Scheduler.get_all_conflicts()` - Conflicts across all pets

### 4. **Recurring Task Generation** (1 method)
- `Task.get_next_occurrence()` - Generate next daily/weekly instance

### 5. **Core Utilities** (4+ methods)
- `Task.complete()` - Mark done + set timestamp
- `Task.is_overdue()` - Check if past deadline
- `Pet.add_task(task)` - Add to task list
- `Owner.add_pet(pet)` - Add to pet collection

---

## Edge Cases Identified (20+ scenarios)

### Empty/None Cases
- ✓ Pet with NO tasks → sorting/filtering returns `[]`
- ✓ Task with `scheduled_at=None` → placed at end in sorting
- ✓ Task with `frequency=None` → `get_next_occurrence()` returns `None`
- ✓ Owner with NO pets → `get_all_tasks()` returns `[]`

### Boundary Conditions
- ✓ Two tasks at EXACT same time → sort is deterministic (no crash)
- ✓ Back-to-back tasks (end_time = next_start_time) → NO conflict
- ✓ Task completed AT exact deadline → `is_overdue()` = `False`
- ✓ Task with unknown priority string → treated as "low"
- ✓ Task with zero `duration_minutes` → filtered out in conflict detection

### Complex Scenarios
- ✓ 3+ tasks all overlapping → correctly identify all pair conflicts
- ✓ Mixed priorities in same time slot → priority sort is deterministic
- ✓ Recurring task marked complete → next instance is trackable
- ✓ Multi-pet scheduling → Owner methods aggregate correctly
- ✓ Daily task crosses midnight → timedelta(days=1) still works

---

## Current Test Coverage

**Existing Tests: 18 passing ✓**
- Task completion (3 tests)
- Task addition (3 tests)
- PetFood (4 tests)
- Owner & pets (3 tests)
- Scheduler (2 tests)
- TimelyCare (3 tests)

**Tests Needed: ~20 additional tests**
- Sorting edge cases (5 tests)
- Filtering edge cases (5 tests)
- Conflict detection (5 tests)
- Recurring task generation (5 tests)

**Target: 38+ total tests with >90% coverage**

---

## AI Prompts Ready for Use

### Prompt 1: Sorting Algorithm Tests
```
I have a Pet class with sorting methods:
- get_tasks_sorted_by_time(): O(n log n) sort by scheduled_at
- get_tasks_sorted_by_priority(): O(n log n) sort by priority then time

Edge cases:
1. Empty pet (no tasks)
2. Tasks with scheduled_at=None (should go to end)
3. All tasks at exact same time
4. Single task
5. Unknown priority string

Can you write 5 pytest test methods that cover these? Use the Arrange-Act-Assert pattern.
```

### Prompt 2: Filtering Algorithm Tests
```
I have Pet class with filtering methods:
- get_tasks_by_status(completed): bool filter
- get_high_priority_tasks(): filter for priority=="high"
- get_recurring_tasks(): filter for frequency is not None
- get_pending_tasks(): filter for completed==False

Edge cases:
1. No tasks match the filter (return [])
2. All tasks match the filter (return all)
3. Pet with no tasks at all
4. Mix of matching and non-matching tasks

Can you write 4 pytest test methods covering these?
```

### Prompt 3: Conflict Detection Tests
```
I have a Scheduler.detect_conflicts_for_pet(pet) method that finds overlapping tasks using:
  task1.start < task2.end AND task2.start < task1.end

Edge cases:
1. Pet with no tasks (should return [])
2. Pet with 1 task (can't conflict with itself, return [])
3. Tasks with None scheduled_at (filtered out, return [])
4. Tasks with 0 duration_minutes (filtered out)
5. Back-to-back tasks at exact same time boundary (should NOT conflict)
6. Three tasks all overlapping (should find all 3 pair conflicts)

Can you write 6 pytest tests covering these?
```

### Prompt 4: Recurring Task Generation Tests
```
I have a Task.get_next_occurrence() method that:
- Returns None if frequency is None or scheduled_at is None
- For frequency="daily": returns new Task with scheduled_at + timedelta(days=1)
- For frequency="weekly": returns new Task with scheduled_at + timedelta(days=7)
- Generated task has parent_recurring_id set to track lineage

Edge cases:
1. Non-recurring task (frequency=None)
2. Unscheduled task (scheduled_at=None)
3. Unknown frequency string (e.g., "monthly")
4. Daily task should generate with correct date math
5. Weekly task should generate with correct date math
6. New task has unique ID (different from parent)
7. New task has parent_recurring_id pointing to parent

Can you write 7 pytest tests covering these?
```

---

## Test Plan Document Created

📄 **FILE: TEST_PLAN_PHASE6.md**
- Complete methodology for testing all 5 behavior categories
- Example test code structure (Arrange-Act-Assert)
- Sample test implementations
- AI prompt templates ready to use
- Coverage goals and verification checklist

---

## Ready for Step 2: Test Generation

You now have:
1. ✅ **Core behaviors identified**: 21 methods across 5 categories
2. ✅ **Edge cases catalogued**: 20+ scenarios with specific criteria
3. ✅ **Test plan documented**: Detailed methodology in TEST_PLAN_PHASE6.md
4. ✅ **AI prompts prepared**: 4 focused prompts ready for AI test generation

**Next**: Use these AI prompts to generate comprehensive test cases!

### Recommended Next Step

Copy **Prompt 1** (Sorting Algorithm Tests) and paste it into your AI coding assistant with:
- Reference to the test file
- Any specific assert style preferences
- Whether you want parametrized tests or individual test methods

The AI will generate pytest code that you can directly add to `tests/test_pawpal.py`.

