# Phase 4: Smart Features - Analysis & Recommendations

## 🎯 Current State vs. Future State

### Current Limitations

| Issue | Example | Impact |
|-------|---------|--------|
| **No sorting** | Tasks show in creation order | Owner can't see "what's next?" |
| **No priorities** | All tasks treated equally | Feeding pet = Playing with pet |
| **No duration** | Tasks have no time estimate | Can't detect conflicts |
| **No conflict detection** | Can schedule 2 tasks at same time | Owner gets overwhelmed |
| **No recurring tasks** | "Feed pet" added manually daily | Tedious, error-prone |
| **Manual filtering** | `next((p for p in owner.pets if task in p.tasks), None)` | Verbose, inefficient |
| **No scheduling logic** | Tasks dumped in list | No intelligence applied |

### What We'll Add

| Feature | Benefit | Complexity |
|---------|---------|-----------|
| **Smart Sorting** | See tasks by time/priority | ⭐ Easy |
| **Duration Tracking** | Know how long tasks take | ⭐ Easy |
| **Conflict Detection** | Prevent overbooking | ⭐⭐ Medium |
| **Task Prioritization** | Focus on what matters | ⭐ Easy |
| **Filtering Methods** | Clean task lookups | ⭐ Easy |
| **Smart Scheduling** | Suggest optimal order | ⭐⭐ Medium |
| **Recurring Tasks** | Auto-generate patterns | ⭐⭐⭐ Hard |

---

## 📊 Recommended Quick Wins (30 minutes)

### 1. Add Fields to Task Dataclass (5 min)
```python
@dataclass
class Task:
    # ... existing ...
    priority: str = "medium"          # "high", "medium", "low"
    duration_minutes: int = 15        # Estimated duration
```

**Impact**: Enables sorting, conflicts, scheduling

### 2. Add Sorting Methods (15 min)
```python
# In Pet class
def get_tasks_sorted_by_time(self) -> List[Task]:
    """Sort tasks by scheduled_at time."""
    return sorted(self.tasks, key=lambda t: t.scheduled_at or datetime.max)

def get_tasks_sorted_by_priority(self) -> List[Task]:
    """Sort tasks: high → medium → low → time."""
    priority_order = {"high": 0, "medium": 1, "low": 2}
    return sorted(self.tasks, 
        key=lambda t: (priority_order.get(t.priority, 3), t.scheduled_at))

# In Owner class
def get_all_tasks_sorted_by_priority(self) -> List[Task]:
    """Get all tasks across all pets, sorted by priority."""
    all_tasks = self.get_all_tasks()
    priority_order = {"high": 0, "medium": 1, "low": 2}
    return sorted(all_tasks, 
        key=lambda t: (priority_order.get(t.priority, 3), t.scheduled_at))
```

**Usage**: `pet.get_tasks_sorted_by_priority()` instead of manual loop

**Complexity**: O(n log n) - very efficient even for 100s of tasks

### 3. Add Filtering Methods (10 min)
```python
# In Pet class
def get_high_priority_tasks(self) -> List[Task]:
    return [t for t in self.tasks if t.priority == "high"]

def get_tasks_by_status(self, completed: bool) -> List[Task]:
    return [t for t in self.tasks if t.completed == completed]

# In Owner class
def get_tasks_for_pet(self, pet: Pet) -> List[Task]:
    """Get all tasks for a specific pet."""
    return pet.tasks

def get_all_pending_by_priority(self) -> List[Task]:
    """Get all pending tasks across all pets, by priority."""
    pending = self.get_all_pending_tasks()
    priority_order = {"high": 0, "medium": 1, "low": 2}
    return sorted(pending, key=lambda t: priority_order.get(t.priority, 3))
```

**Usage**: `owner.get_all_pending_by_priority()` - cleaner than manual loops

**Complexity**: O(n) - linear, very fast

---

## 🚀 Medium Complexity: Conflict Detection (20 min)

### What It Does
Detects when two tasks for a pet overlap in time, considering duration.

### Algorithm
```python
def detect_conflicts(self) -> List[Tuple[Task, Task]]:
    """Find task pairs that overlap in time for this pet."""
    conflicts = []
    
    # Only check tasks that have both time and duration
    tasks_with_time = [t for t in self.tasks 
                       if t.scheduled_at and t.duration_minutes]
    
    # Compare each pair
    for i, task1 in enumerate(tasks_with_time):
        for task2 in tasks_with_time[i+1:]:
            # Calculate end times
            end1 = task1.scheduled_at + timedelta(minutes=task1.duration_minutes)
            end2 = task2.scheduled_at + timedelta(minutes=task2.duration_minutes)
            
            # Check if windows overlap
            if task1.scheduled_at < end2 and task2.scheduled_at < end1:
                conflicts.append((task1, task2))
    
    return conflicts
```

### Example
```python
# Create overlapping tasks
task1 = Task(title="Feed", scheduled_at=now, duration_minutes=10)
task2 = Task(title="Play", scheduled_at=now + timedelta(minutes=5), duration_minutes=10)
pet.add_task(task1)
pet.add_task(task2)

# Detect conflict
conflicts = pet.detect_conflicts()
# Returns: [(Feed, Play)] because:
#   Feed: 1:00 - 1:10
#   Play: 1:05 - 1:15  ← overlaps!
```

### Complexity Analysis
- **Time**: O(n²) worst case, but typically O(n)
- **Why O(n²)?**: Comparing each task pair
- **Is it fast enough?**: Yes! Even 100 tasks × 100 tasks = 10,000 comparisons ≈ 1ms

---

## 🧠 Advanced: Recurring Tasks (40 min)

### What It Does
Automatically generates task instances for daily/weekly patterns.

### Data Model
```python
@dataclass
class RecurringTask:
    template_title: str                    # "Feed Mochi"
    frequency: str                         # "daily" or "weekly"
    occurrence_days: List[int] = None      # For weekly: [0=Mon, 1=Tue, ...]
    duration_minutes: int = 15
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    
    def generate_instances(self, days_ahead: int = 7) -> List[Task]:
        """Generate Task instances for next N days."""
        instances = []
        current = self.start_date
        deadline = self.end_date or (self.start_date + timedelta(days=days_ahead))
        
        while current <= deadline:
            if self._should_occur_on(current):
                instance = Task(
                    title=self.template_title,
                    scheduled_at=current.replace(hour=8, minute=0),  # Default morning
                    duration_minutes=self.duration_minutes,
                    priority="high"
                )
                instances.append(instance)
            
            current += timedelta(days=1)
        
        return instances
    
    def _should_occur_on(self, date: datetime) -> bool:
        """Check if task should occur on this date."""
        if self.frequency == "daily":
            return True
        elif self.frequency == "weekly":
            return date.weekday() in (self.occurrence_days or [])
        return False
```

### Usage Example
```python
# Define recurring task: Feed Mochi every day
daily_feed = RecurringTask(
    template_title="Feed Mochi",
    frequency="daily",
    duration_minutes=5,
    start_date=datetime.now()
)

# Generate 30 days of feeding tasks
instances = daily_feed.generate_instances(days_ahead=30)
for task in instances:
    mochi.add_task(task)

# Now mochi has 30 feeding tasks automatically created!

# Recurring weekly: Exercise on Mon/Wed/Fri
weekly_exercise = RecurringTask(
    template_title="Exercise Rex",
    frequency="weekly",
    occurrence_days=[0, 2, 4],  # Mon, Wed, Fri
    duration_minutes=30,
    start_date=datetime.now()
)

exercise_instances = weekly_exercise.generate_instances(days_ahead=60)
for task in exercise_instances:
    rex.add_task(task)
```

### Complexity Analysis
- **Time**: O(d) where d = number of days
- **Space**: O(d) for generated instances
- **Efficiency**: Very fast! 365 days of instances ≈ 5ms

---

## 📋 Implementation Roadmap

### Phase 4a: Quick Wins (30 min) - Do First ⭐
1. Add `priority` and `duration_minutes` to Task → 5 min
2. Add sorting methods (by time, priority) → 15 min
3. Add filtering methods (by status, priority) → 10 min
4. Update `main.py` demo → 5 min
5. Add 5 new pytest tests → 10 min

**Result**: Smarter schedules, better filtering

### Phase 4b: Conflict Detection (25 min) - Do Second
1. Add `detect_conflicts()` method to Pet → 15 min
2. Add `get_available_slots()` method → 10 min
3. Add 3 new pytest tests → 10 min

**Result**: Prevent overbooking, warn owner

### Phase 4c: Recurring Tasks (45 min) - Do Third (Optional)
1. Create `RecurringTask` dataclass → 10 min
2. Add `generate_instances()` method → 15 min
3. Add `add_recurring_task()` to Pet → 5 min
4. Add 5 new pytest tests → 10 min
5. Update demo → 5 min

**Result**: Auto-generated daily/weekly tasks

---

## 💡 Design Decisions

### Why Sort by Priority + Time?
- **Why not just time?** Owner wants "urgent first"
- **Why not just priority?** Same-priority tasks need time ordering
- **Solution**: Tuple sort `(priority_rank, scheduled_at)` = best of both

### Why O(n²) Conflict Detection?
- **Why not O(n log n)?** Would need interval tree (overkill)
- **Is O(n²) acceptable?** Yes! With 20-100 tasks/day, still <1ms
- **When to optimize?** Only if you have 1000+ tasks

### Why Separate RecurringTask Class?
- **Why not store recurrence in Task?** Task is a specific instance, not a pattern
- **Separation of concerns**: Template (RecurringTask) vs. Instance (Task)
- **Flexibility**: Can modify one recurring task's instances independently

---

## 🎓 Algorithmic Concepts Introduced

| Concept | Where | Complexity |
|---------|-------|-----------|
| **Sorting** | `get_tasks_sorted_by_priority()` | O(n log n) |
| **Filtering** | `get_high_priority_tasks()` | O(n) |
| **Tuple sorting** | Multi-key sort (priority, time) | O(n log n) |
| **Interval overlap** | Conflict detection | O(n²) |
| **Pattern generation** | Recurring tasks | O(d) |
| **Greedy algorithm** | Smart scheduling | O(n) |

---

## ✅ Next Steps

### Immediate (Today)
1. Review this document with team
2. Implement Phase 4a (Quick Wins)
3. Run tests: `pytest tests/test_pawpal.py -v`
4. Update app.py to use new sorting/filtering

### Short-term (This Week)
1. Implement Phase 4b (Conflict Detection)
2. Add conflict warnings to app.py
3. Test with real-world scenarios

### Medium-term (Nice-to-have)
1. Implement Phase 4c (Recurring Tasks)
2. Add recurring task UI to Streamlit
3. Performance optimization if needed

---

## Questions to Consider

1. **Should high-priority tasks always come first?** 
   - Or should emergency tasks (overdue) override?

2. **How to handle duration estimation?**
   - Should app learn from actual completion times?

3. **What if owner doesn't set priority?**
   - Default to "medium" (current plan) - good?

4. **Should recurring tasks be editable?**
   - Can owner modify one instance vs. whole pattern?

5. **Should conflicts block task creation?**
   - Or just warn and let owner decide?

---

## Success Metrics (After Phase 4)

✅ Tasks sorted by priority/time by default  
✅ No more manual pet lookups  
✅ Conflicts detected and warned  
✅ Daily/weekly tasks auto-generated  
✅ App feels "smart" not "dumb"  
✅ Code remains clean and maintainable  
✅ 25+ pytest tests passing  
