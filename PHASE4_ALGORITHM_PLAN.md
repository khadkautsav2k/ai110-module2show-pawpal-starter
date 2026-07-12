# Phase 4: Algorithmic Improvements & Smart Features

## Current State Analysis

### What Works
✅ Task creation and storage  
✅ Task completion with timestamps  
✅ Basic filtering (today's tasks, pending tasks)  
✅ Food inventory tracking  
✅ Owner ↔ Pet ↔ Task relationships  

### What Feels Manual/Inefficient

1. **No Task Sorting**: Tasks display in creation order, not by priority or time
   - Current: `[Feed Mochi, Play, Clean bowls]` (random)
   - Better: `[Clean bowls 2pm, Feed Mochi 1pm, Play 3pm]` (sorted by time)

2. **No Conflict Detection**: Can assign tasks at overlapping times
   - Current: Two 2-hour tasks can be scheduled simultaneously
   - Better: Warn when tasks overlap or owner is overbooked

3. **No Recurring Tasks**: Each task is a one-off
   - Current: "Feed Mochi" must be added manually every day
   - Better: Mark as recurring daily/weekly, auto-generate instances

4. **No Task Prioritization**: All tasks treated equally
   - Current: Feeding (critical) and playing (nice-to-have) same priority
   - Better: Sort by priority (high/medium/low)

5. **No Pet-Based Filtering**: Can't easily see only tasks for one pet
   - Current: Must loop through all tasks, find pet matches
   - Better: `owner.get_tasks_for_pet(pet)` → fast lookup

6. **No Duration Tracking**: Tasks have no duration (hours/minutes)
   - Current: "Feed Mochi" is instant? 5 min? 30 min?
   - Better: Estimate duration for conflict detection

7. **Manual Pet Lookup**: Finding which pet owns a task is verbose
   - Current: `next((p for p in owner.pets if task in p.tasks), None)`
   - Better: `task.pet` back-reference or `owner.get_pet_for_task(task)`

8. **No Scheduling Intelligence**: Schedule doesn't account for constraints
   - Current: Dump all tasks sorted by time
   - Better: Smart scheduling respecting duration, conflicts, priorities

---

## Proposed Algorithms (Phase 4)

### 1. **Task Sorting Algorithm** 🔄
**Purpose**: Sort tasks intelligently instead of random order

**Options**:
- **A) Sort by time only**
  ```python
  def get_sorted_tasks(self) -> List[Task]:
      return sorted(self.tasks, key=lambda t: t.scheduled_at or datetime.max)
  ```
  - ✅ Simple, fast (O(n log n))
  - ❌ Doesn't account for priority
  - **Use case**: Timeline view, "what's next?"

- **B) Sort by priority then time** (Multi-key sort)
  ```python
  def get_sorted_tasks(self, prioritize=True) -> List[Task]:
      priority_order = {"high": 0, "medium": 1, "low": 2}
      return sorted(self.tasks, 
          key=lambda t: (priority_order.get(t.priority, 3), t.scheduled_at))
  ```
  - ✅ Respects both priority and time
  - ⚠️ Assumes Task has priority field (needs adding)
  - **Use case**: "What should I do first?"

- **C) Sort by duration + priority** (For conflict detection prep)
  ```python
  def get_sorted_by_duration(self) -> List[Task]:
      return sorted(self.tasks, 
          key=lambda t: (-t.duration_minutes, -priority_score(t)))
  ```
  - ✅ Handles scheduling constraints
  - ⚠️ Requires duration_minutes field
  - **Use case**: "Can I fit all tasks today?"

**Recommendation**: Implement **Option B** (priority + time) - most useful for pet owners

---

### 2. **Conflict Detection Algorithm** ⚠️
**Purpose**: Detect overlapping tasks and time conflicts

**Algorithm**:
```python
def detect_conflicts(self, pet: Pet) -> List[Tuple[Task, Task]]:
    """Find tasks for a pet that overlap in time."""
    conflicts = []
    tasks_with_time = [t for t in pet.tasks if t.scheduled_at and t.duration_minutes]
    
    for i, task1 in enumerate(tasks_with_time):
        for task2 in tasks_with_time[i+1:]:
            # Check if time windows overlap
            end1 = task1.scheduled_at + timedelta(minutes=task1.duration_minutes)
            end2 = task2.scheduled_at + timedelta(minutes=task2.duration_minutes)
            
            if task1.scheduled_at < end2 and task2.scheduled_at < end1:
                conflicts.append((task1, task2))
    
    return conflicts
```

**Complexity**: O(n²) but acceptable for typical pet owners (10-20 tasks/day)

**Features**:
- ✅ Find overlaps per pet
- ✅ Account for duration
- ⚠️ Assumes Task.duration_minutes field exists

---

### 3. **Recurring Tasks Algorithm** 🔁
**Purpose**: Auto-generate task instances for repeating patterns

**Data Model**:
```python
@dataclass
class RecurringTask:
    template_title: str
    frequency: str  # "daily", "weekly", "every_N_days"
    occurrence_pattern: List[int]  # days of week: [0=Mon, 6=Sun]
    start_date: datetime
    end_date: Optional[datetime]
    duration_minutes: int
    
    def generate_instances(self, days_ahead=7) -> List[Task]:
        """Generate Task instances for next N days."""
        instances = []
        current = self.start_date
        
        while current <= (self.end_date or current + timedelta(days=days_ahead)):
            if self._should_occur_on(current):
                task = Task(
                    title=self.template_title,
                    scheduled_at=current,
                    duration_minutes=self.duration_minutes
                )
                instances.append(task)
            current += timedelta(days=1)
        
        return instances
    
    def _should_occur_on(self, date: datetime) -> bool:
        """Check if task should occur on this date."""
        if self.frequency == "daily":
            return True
        elif self.frequency == "weekly":
            return date.weekday() in self.occurrence_pattern
        return False
```

**Complexity**: O(n days) - linear, very fast

**Features**:
- ✅ Daily, weekly, custom patterns
- ✅ Auto-generates instances ahead of time
- ✅ Can set end date for temporary recurring tasks

---

### 4. **Pet-Based Filtering Algorithm** 🐾
**Purpose**: Fast lookup of tasks for a specific pet

**Option A: Method on Pet class**
```python
def get_tasks_by_status(self, completed: bool = False) -> List[Task]:
    return [t for t in self.tasks if t.completed == completed]

def get_overdue_tasks(self) -> List[Task]:
    return [t for t in self.tasks if t.is_overdue()]
```

**Option B: Reverse lookup via Owner**
```python
def get_tasks_for_pet(self, pet: Pet) -> List[Task]:
    """Get all tasks for a specific pet."""
    return pet.tasks

def get_pending_tasks_for_pet(self, pet: Pet) -> List[Task]:
    return [t for t in pet.tasks if not t.completed]
```

**Recommendation**: Implement **both** - flexible & efficient

---

### 5. **Smart Schedule Suggestion Algorithm** 🧠
**Purpose**: Suggest optimal task ordering based on constraints

**Algorithm** (Greedy + Priority):
```python
def suggest_optimal_schedule(self, pet: Pet, start_time: datetime, 
                            available_minutes: int) -> List[Task]:
    """Suggest task order that fits in available time."""
    pending = pet.get_pending_tasks()
    pending_sorted = sorted(pending, 
        key=lambda t: (-priority_score(t), t.scheduled_at))
    
    schedule = []
    current_time = start_time
    remaining_time = available_minutes
    
    for task in pending_sorted:
        if task.duration_minutes and task.duration_minutes <= remaining_time:
            schedule.append(task)
            remaining_time -= task.duration_minutes
            current_time += timedelta(minutes=task.duration_minutes)
        # Skip task if not enough time
    
    return schedule
```

**Complexity**: O(n log n) due to sorting

**Features**:
- ✅ Respects available time
- ✅ Prioritizes high-priority tasks
- ✅ Greedy algorithm (fast, good-enough solution)

---

## Implementation Priority (Easiest to Hardest)

| Priority | Feature | Difficulty | Time | Impact |
|----------|---------|-----------|------|--------|
| 1️⃣ | Task sorting by time | ⭐ Easy | 10 min | High (immediate use) |
| 2️⃣ | Task filtering by pet/status | ⭐ Easy | 10 min | High (cleaner UI) |
| 3️⃣ | Add duration_minutes field | ⭐ Easy | 5 min | Medium (needed for conflicts) |
| 4️⃣ | Conflict detection | ⭐⭐ Medium | 20 min | High (prevents overbooking) |
| 5️⃣ | Add priority field | ⭐ Easy | 10 min | Medium (better prioritization) |
| 6️⃣ | Sort by priority + time | ⭐⭐ Medium | 15 min | High (smarter schedules) |
| 7️⃣ | Smart schedule suggestion | ⭐⭐ Medium | 25 min | Medium (scheduling help) |
| 8️⃣ | Recurring tasks framework | ⭐⭐⭐ Hard | 40 min | High (reduces manual work) |

---

## Phase 4 Implementation Plan

### **Step 1: Add Missing Fields to Task** (5 min)
```python
@dataclass
class Task:
    # ... existing fields ...
    priority: str = "medium"  # "high", "medium", "low"
    duration_minutes: int = 15  # Estimated duration
```

### **Step 2: Add Sorting Methods** (15 min)
```python
# In Pet class
def get_tasks_sorted_by_time(self) -> List[Task]:
def get_tasks_sorted_by_priority(self) -> List[Task]:

# In Owner class
def get_all_tasks_sorted(self, by="time") -> List[Task]:
```

### **Step 3: Add Filtering Methods** (10 min)
```python
# In Pet class
def get_pending_tasks(self) -> List[Task]:  # Already exists
def get_high_priority_tasks(self) -> List[Task]:
def get_overdue_tasks(self) -> List[Task]:

# In Owner class
def get_tasks_for_pet(self, pet: Pet) -> List[Task]:
```

### **Step 4: Implement Conflict Detection** (20 min)
```python
# In Pet class
def detect_conflicts(self) -> List[Tuple[Task, Task]]:
def get_available_time_slots(self, date: datetime) -> List[Tuple[datetime, datetime]]:

# In Scheduler class
def check_overbooked_pet(self, pet: Pet, date: datetime) -> bool:
```

### **Step 5: Add Smart Scheduling** (25 min)
```python
# In Scheduler class
def suggest_task_order(self, pet: Pet, max_duration_minutes: int) -> List[Task]:
def get_recommended_schedule(self) -> Dict[Pet, List[Task]]:
```

### **Step 6: Implement Recurring Tasks** (40 min)
```python
# New RecurringTask class
@dataclass
class RecurringTask:
    template_title: str
    frequency: str
    # ... other fields ...
    
    def generate_instances(self, days_ahead: int) -> List[Task]:

# In Pet class
def add_recurring_task(self, recurring: RecurringTask) -> None:
def generate_recurring_instances(self, days_ahead: int = 7) -> List[Task]:
```

---

## Tests to Add (pytest)

```python
def test_sort_tasks_by_time():
    """Verify tasks sort by scheduled_at time."""
    
def test_sort_tasks_by_priority():
    """Verify tasks sort high→medium→low."""
    
def test_detect_conflicts():
    """Verify overlapping tasks detected."""
    
def test_no_conflicts_with_gap():
    """Verify non-overlapping tasks pass."""
    
def test_recurring_task_generation():
    """Verify daily/weekly patterns generate correctly."""
    
def test_smart_schedule_respects_duration():
    """Verify schedule doesn't exceed max time."""
    
def test_filter_tasks_by_pet():
    """Verify owner.get_tasks_for_pet() works."""
```

---

## Example Usage (Post-Phase 4)

```python
# Smart sorting
scheduler = Scheduler(owner=owner)
sorted_tasks = scheduler.owner.get_all_tasks_sorted(by="priority_time")
# Output: High-priority tasks first, then sorted by time

# Conflict detection
pet = owner.pets[0]
conflicts = pet.detect_conflicts()
if conflicts:
    print(f"⚠️ {len(conflicts)} task conflicts found!")
    for task1, task2 in conflicts:
        print(f"  {task1.title} overlaps with {task2.title}")

# Recurring tasks
daily_feeding = RecurringTask(
    template_title="Feed Mochi",
    frequency="daily",
    duration_minutes=5,
    start_date=datetime.now()
)
feed_instances = daily_feeding.generate_instances(days_ahead=30)
for instance in feed_instances:
    pet.add_task(instance)

# Smart scheduling
pet = owner.pets[0]
optimal_order = scheduler.suggest_task_order(pet, max_duration_minutes=120)
print("Suggested task order (fits in 2 hours):")
for i, task in enumerate(optimal_order, 1):
    print(f"  {i}. {task.title} ({task.duration_minutes} min)")
```

---

## Success Criteria (Phase 4 Complete)

✅ Tasks can be sorted by time, priority, or duration  
✅ Conflicts detected when tasks overlap  
✅ Recurring patterns (daily/weekly) supported  
✅ Can filter tasks by pet, status, priority  
✅ Smart scheduler suggests optimal task order  
✅ All new features covered by pytest tests  
✅ app.py updated to use new sorting/filtering  
✅ Documented with examples  

---

## Recommendation: Start with Steps 1-3

These give **immediate value** with minimal complexity:
1. Add duration_minutes + priority fields → 5 min
2. Add sorting methods → 15 min
3. Add filtering methods → 10 min

**Result**: Smarter, cleaner schedules with ~30 minutes of work!

Then tackle conflict detection (Step 4) for robustness.
