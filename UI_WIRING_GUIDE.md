# Step 3: Wiring UI Actions to Logic

## Overview
Your Streamlit UI is now fully connected to your backend classes. Here's how each UI action triggers the corresponding class method:

---

## 1. Add Pet Flow

### UI Component
```python
if st.button("Add Pet"):
    new_pet = Pet(name=pet_name, species=species)
    st.session_state.owner.add_pet(new_pet)
```

### Backend Method Called
- **Class**: `Owner`
- **Method**: `add_pet(pet: Pet) -> None`
- **What it does**: Appends the Pet to the Owner's pets list

### Data Flow
```
User Input (pet_name, species)
    ↓
Create Pet object: Pet(name, species)
    ↓
Call: Owner.add_pet(pet)
    ↓
Pet added to st.session_state.owner.pets
    ↓
Page rerun via st.rerun() shows updated pet list
```

---

## 2. Select Pet & Add Task Flow

### UI Component
```python
pet_names = [f"{i+1}. {p.name} ({p.species})" for i, p in enumerate(st.session_state.owner.pets)]
selected_pet_display = st.selectbox("Select a pet to add tasks:", pet_names)
```

### Backend Method Called
- **Class**: `Pet`
- **Method**: `add_task(task: Task) -> None`
- **What it does**: Appends the Task to the Pet's tasks list

### Data Flow
```
User Input (task_title, duration, priority)
    ↓
Create Task object: Task(title, description, scheduled_at)
    ↓
Get selected pet from: st.session_state.selected_pet
    ↓
Call: selected_pet.add_task(task)
    ↓
Task added to Pet.tasks (which is in st.session_state.owner.pets)
    ↓
Page rerun shows task in selected pet's task list
```

---

## 3. Mark Task Complete Flow

### UI Component
```python
if st.button(f"Mark '{task.title}' complete", key=f"complete_{task.id}"):
    task.complete()
```

### Backend Method Called
- **Class**: `Task`
- **Method**: `complete() -> None`
- **What it does**: Sets `completed = True` and `completed_at = datetime.now()`

### Data Flow
```
User clicks "Mark complete" button
    ↓
Call: task.complete()
    ↓
Task.completed = True
Task.completed_at = datetime.now()
    ↓
Page rerun shows updated task status with ✅
```

---

## 4. Generate Schedule Flow

### UI Component
```python
if st.button("Generate Today's Schedule"):
    scheduler = Scheduler(owner=st.session_state.owner)
    todays_tasks = scheduler.get_todays_schedule()
    pending_tasks = scheduler.get_pending_tasks()
    overdue_tasks = scheduler.get_tasks_to_execute()
```

### Backend Methods Called
- **Class**: `Scheduler`
- **Methods**:
  - `get_todays_schedule() -> List[Task]`
  - `get_pending_tasks() -> List[Task]`
  - `get_tasks_to_execute() -> List[Task]` (overdue)

### Data Flow
```
User clicks "Generate Today's Schedule"
    ↓
Create Scheduler: Scheduler(owner=st.session_state.owner)
    ↓
Call: scheduler.get_todays_schedule()
    ├─ Iterates through all pets in owner.pets
    ├─ Collects all tasks scheduled for today
    └─ Returns sorted by scheduled_at time
    ↓
Call: scheduler.get_pending_tasks()
    ├─ Calls owner.get_all_pending_tasks()
    ├─ Returns all tasks where completed == False
    └─ Across all pets
    ↓
Call: scheduler.get_tasks_to_execute()
    ├─ Returns overdue tasks
    ├─ Only incomplete tasks past their scheduled time
    └─ Prioritized for immediate action
    ↓
Display results in expandable sections with status indicators
```

---

## Key Design Patterns

### 1. **Persistent Objects in Session State**
Objects stored in `st.session_state` survive page reruns and allow modifications:
```python
st.session_state.owner.add_pet(new_pet)  # Modifies the persisted object
```

### 2. **Method Chaining through the Object Graph**
Operations flow through your class hierarchy:
```
UI Button
  → Create object (Pet, Task, etc.)
  → Call method on that object
  → Which may call methods on related objects (owner.add_pet)
  → All stored in session_state for persistence
```

### 3. **Rerun Pattern**
After modifying data, `st.rerun()` refreshes the UI:
```python
st.session_state.owner.add_pet(new_pet)
st.rerun()  # Reruns script, shows updated list
```

### 4. **Aggregation Pattern (Owner/Scheduler)**
The Owner and Scheduler aggregate data from multiple pets:
```python
owner.get_all_tasks()  # Collects tasks from ALL pets
scheduler.get_todays_schedule()  # Filters across all pets for today
```

---

## Class Methods Used

| UI Action | Class | Method | Returns |
|-----------|-------|--------|---------|
| Add Pet | `Owner` | `add_pet(pet)` | None |
| Add Task | `Pet` | `add_task(task)` | None |
| Mark Complete | `Task` | `complete()` | None |
| Generate Schedule | `Owner` | `get_all_tasks()` | List[Task] |
| Filter Today | `Scheduler` | `get_todays_schedule()` | List[Task] |
| Filter Pending | `Owner` | `get_all_pending_tasks()` | List[Task] |
| Check Overdue | `Task` | `is_overdue()` | bool |

---

## Verification

All UI actions now call real backend methods:
- ✅ Pet creation uses `Pet(name, species)` dataclass
- ✅ Pet addition uses `Owner.add_pet()` method
- ✅ Task creation uses `Task(title, description, scheduled_at)` dataclass
- ✅ Task addition uses `Pet.add_task()` method
- ✅ Task completion uses `Task.complete()` method (with timestamp)
- ✅ Schedule generation uses `Scheduler` logic
- ✅ All data persists in `st.session_state`

Try the app now with: `streamlit run app.py`
