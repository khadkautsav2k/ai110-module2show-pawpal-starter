# Test Plan for PawPal+ Scheduler

## Phase 6: Testing & Verification

### Overview
This document outlines the comprehensive test strategy for PawPal+, focusing on core behaviors and edge cases for the Phase 4 scheduling algorithms (sorting, filtering, conflict detection, recurring tasks).

---

## Step 1: Core Behaviors to Test

### 1. **Sorting Algorithms**
**What to verify:** Tasks are correctly ordered by time and priority

**Happy Path:**
- Multiple tasks with different scheduled times → should sort earliest first
- Multiple tasks with same priority → secondary sort by time works
- Tasks with high/medium/low priorities → should follow priority order

**Edge Cases:**
- Pet with NO tasks → returns empty list (no error)
- Tasks with unscheduled time (None) → placed at end, sorted after scheduled tasks
- All tasks at exact same time → maintain order, don't crash
- Single task → returns list with 1 item
- Tasks with unknown priority → treated as low priority

**Test Methods:**
- `Pet.get_tasks_sorted_by_time()`
- `Pet.get_tasks_sorted_by_priority()`
- `Scheduler.get_todays_schedule()`
- `Scheduler.get_todays_schedule_by_priority()`
- `Owner.get_all_tasks_sorted_by_time()`
- `Owner.get_all_tasks_sorted_by_priority()`

---

### 2. **Filtering Algorithms**
**What to verify:** Correct tasks are selected based on predicate

**Happy Path:**
- Filter by status (pending vs completed) → returns only matching tasks
- Filter high-priority → returns only high-priority tasks
- Filter recurring → returns only daily/weekly tasks
- Multiple pets → filter works across all pets

**Edge Cases:**
- No tasks match filter → returns empty list
- All tasks match filter → returns all tasks
- Pet with no tasks at all → returns empty list, no error
- Mixed filters (pending + high-priority) → should combine correctly
- Task with unset priority → treated as "medium" by default

**Test Methods:**
- `Pet.get_tasks_by_status(completed)`
- `Pet.get_high_priority_tasks()`
- `Pet.get_recurring_tasks()`
- `Pet.get_pending_tasks()`
- `Owner.get_all_pending_tasks()`
- `Owner.get_all_overdue_tasks()`
- `Owner.get_all_high_priority_tasks()`
- `Owner.get_all_pending_by_priority()`

---

### 3. **Conflict Detection Algorithm**
**What to verify:** Overlapping tasks are correctly identified

**Happy Path:**
- Two tasks at exact same time → conflict detected
- Task1: 2:00pm-2:15pm, Task2: 2:10pm-2:25pm → conflict (overlap)
- Task1: 2:00pm-2:10pm, Task2: 2:10pm-2:20pm → no conflict (back-to-back)
- Task1: 2:00pm, Task2: 3:00pm → no conflict (sequential)

**Edge Cases:**
- Pet with NO tasks → returns empty conflicts list
- Pet with 1 task → returns empty conflicts (need 2+ to conflict)
- Tasks with no scheduled_at (None) → filtered out, no error
- Tasks with zero duration_minutes → filtered out, no error
- 3+ tasks all overlapping → correctly identifies all pair conflicts
- Same task compared to itself → not included (uses i+1 to avoid)

**Test Methods:**
- `Scheduler.detect_conflicts_for_pet(pet)`
- `Scheduler.get_all_conflicts()`

---

### 4. **Recurring Task Generation**
**What to verify:** Next occurrence correctly calculated with proper time arithmetic

**Happy Path:**
- Daily task scheduled 8:00am → next occurrence is 8:00am next day (24h later)
- Weekly task scheduled Tuesday → next occurrence is next Tuesday (7d later)
- Recurring task generates with same properties (title, priority, duration)
- Parent task tracked via parent_recurring_id field

**Edge Cases:**
- Non-recurring task (frequency=None) → get_next_occurrence() returns None
- Unscheduled task (scheduled_at=None) → get_next_occurrence() returns None
- Unknown frequency (e.g., "monthly") → returns None, no crash
- Generated task has new unique ID → different from parent
- Generated task has correct parent_recurring_id → can trace lineage

**Test Methods:**
- `Task.get_next_occurrence()`
- Task.frequency field behavior
- Task.parent_recurring_id tracking

---

### 5. **Task Completion & Overdue Logic**
**What to verify:** Timestamps and status updates work correctly

**Happy Path:**
- Incomplete task past deadline → is_overdue() returns True
- Incomplete task before deadline → is_overdue() returns False
- Completed task regardless of time → is_overdue() returns False
- Task.complete() sets completed_at timestamp

**Edge Cases:**
- Task with no scheduled_at → is_overdue() returns False (can't be overdue without deadline)
- Task completed at exact deadline time → should not be overdue (boundary case)
- Task.completed_at precision → should record datetime accurately

**Test Methods:**
- `Task.complete()`
- `Task.is_overdue()`
- `Pet.get_pending_tasks()`
- `Owner.get_all_overdue_tasks()`

---

## Summary: Test Coverage Matrix

| Category | Happy Path | Edge Cases | Methods |
|----------|-----------|-----------|---------|
| **Sorting** | Correct order | Empty, None, unknown | 6 methods |
| **Filtering** | Correct subset | No matches, all match, empty | 8 methods |
| **Conflicts** | Overlap detected | None, None/0 duration | 2 methods |
| **Recurring** | Next calc correct | Non-recurring, None freq | 1 method |
| **Completion** | Status & time | No deadline, boundary | 5 methods |

---

## Test Execution Strategy

### Current Status
✅ 18 existing tests cover core behaviors (completion, addition, food, owner, scheduler, timely care)

### New Tests Needed (Phase 6)
🟡 Sorting algorithm edge cases (empty list, None values, priority ordering)  
🟡 Filtering edge cases (no matches, mixed predicates)  
🟡 Conflict detection edge cases (no tasks, zero duration, 3+ tasks)  
🟡 Recurring task generation (daily/weekly calculation, parent tracking)  
🟡 Overdue detection boundary cases  

### Recommended Order
1. **Quick wins:** Recurring task generation (simple O(1) logic, easy to test)
2. **Sorting:** Test ordering edge cases (many sorting permutations)
3. **Filtering:** Test predicate combinations (high-priority + pending)
4. **Conflicts:** Test interval overlaps (4-5 scenarios)
5. **Integration:** Test cross-pet scheduling (Owner aggregation)

---

## Example Test Structure

```python
class TestSortingAlgorithms:
    """Test sorting edge cases."""
    
    def test_sort_by_time_empty_list(self):
        """Empty pet with no tasks returns empty list."""
        pet = Pet(name="Mochi", species="Cat")
        result = pet.get_tasks_sorted_by_time()
        assert result == []
    
    def test_sort_by_priority_unscheduled_tasks_at_end(self):
        """Tasks without scheduled_at times appear at end."""
        pet = Pet(name="Biscuit", species="Dog")
        task1 = Task(title="Scheduled", priority="high", 
                     scheduled_at=datetime.now())
        task2 = Task(title="Unscheduled", priority="high", 
                     scheduled_at=None)
        pet.add_task(task2)
        pet.add_task(task1)
        
        result = pet.get_tasks_sorted_by_priority()
        
        assert result[0] == task1  # scheduled first
        assert result[1] == task2  # unscheduled last


class TestConflictDetection:
    """Test conflict detection edge cases."""
    
    def test_no_conflicts_empty_pet(self):
        """Pet with no tasks has no conflicts."""
        scheduler = Scheduler(owner=Owner(name="John"))
        pet = Pet(name="Fluffy", species="Cat")
        
        conflicts = scheduler.detect_conflicts_for_pet(pet)
        
        assert conflicts == []
    
    def test_back_to_back_tasks_no_conflict(self):
        """Tasks ending/starting at exact same time are NOT conflicts."""
        pet = Pet(name="Rex", species="Dog")
        task1 = Task(
            title="Walk", priority="high", duration_minutes=15,
            scheduled_at=datetime(2026, 7, 11, 14, 0)
        )
        task2 = Task(
            title="Feed", priority="high", duration_minutes=10,
            scheduled_at=datetime(2026, 7, 11, 14, 15)
        )
        pet.add_task(task1)
        pet.add_task(task2)
        
        scheduler = Scheduler(owner=Owner(name="Owner"))
        conflicts = scheduler.detect_conflicts_for_pet(pet)
        
        assert conflicts == []  # No conflict (sequential, not overlapping)


class TestRecurringTasks:
    """Test recurring task generation."""
    
    def test_daily_task_next_occurrence(self):
        """Daily task generates next occurrence 24h later."""
        task = Task(
            title="Feed Mochi",
            frequency="daily",
            priority="high",
            duration_minutes=10,
            scheduled_at=datetime(2026, 7, 11, 8, 0)
        )
        
        next_task = task.get_next_occurrence()
        
        assert next_task is not None
        assert next_task.scheduled_at == datetime(2026, 7, 12, 8, 0)
        assert next_task.title == "Feed Mochi"
        assert next_task.frequency == "daily"
        assert next_task.parent_recurring_id == task.id
    
    def test_non_recurring_no_next_occurrence(self):
        """Non-recurring task returns None."""
        task = Task(
            title="One-time task",
            frequency=None,
            scheduled_at=datetime(2026, 7, 11, 8, 0)
        )
        
        next_task = task.get_next_occurrence()
        
        assert next_task is None
```

---

## AI Prompts for Test Generation

When asking your AI coding assistant:

> "I have a pet scheduler with sorting, filtering, conflict detection, and recurring tasks. 
> What are the most important edge cases to test? Focus on:
> 1. Empty lists and None values
> 2. Boundary conditions (exact same time, back-to-back scheduling)
> 3. Multi-key sorting (priority + time)
> 4. Interval overlap detection
> 5. Recurring task date arithmetic with timedelta
> 
> Can you generate pytest test cases for these scenarios?"

---

## Verification Checklist

After implementing tests:

- [ ] All 18 existing tests still pass
- [ ] At least 5 new tests for sorting edge cases
- [ ] At least 5 new tests for filtering edge cases
- [ ] At least 5 new tests for conflict detection edge cases
- [ ] At least 5 new tests for recurring task generation
- [ ] Total test count: 18 + 20 = **38+ tests**
- [ ] All tests have clear docstrings explaining what they verify
- [ ] Edge cases explicitly tested (empty, None, boundary)
- [ ] Code coverage > 90% for pawpal_system.py

---

## Next Steps

1. ✅ **Step 1: Plan** (THIS DOCUMENT) - Identify core behaviors and edge cases
2. 🔄 **Step 2: Generate** - Use AI to write test cases from this plan
3. 🧪 **Step 3: Implement** - Add new tests to test_pawpal.py
4. ✓ **Step 4: Run** - Execute full test suite and verify coverage
5. 📝 **Step 5: Document** - Summarize test results in reflection.md

