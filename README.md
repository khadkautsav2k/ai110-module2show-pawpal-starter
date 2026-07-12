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

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

PawPal+ implements four core scheduling algorithms to make pet care planning intelligent and conflict-free:

| Feature | Method | Algorithm | Complexity |
|---------|--------|-----------|-----------|
| **Sort by Time** | `Pet.get_tasks_sorted_by_time()`, `Scheduler.get_todays_schedule()` | Chronological sort via `sorted(tasks, key=scheduled_at)` | O(n log n) |
| **Sort by Priority** | `Pet.get_tasks_sorted_by_priority()`, `Scheduler.get_todays_schedule_by_priority()` | Multi-key sort: priority rank then time | O(n log n) |
| **Filter by Status** | `Pet.get_tasks_by_status(completed=bool)` | Single-pass predicate filter | O(n) |
| **Filter High Priority** | `Pet.get_high_priority_tasks()`, `Owner.get_all_high_priority_tasks()` | Predicate filter: `priority == "high"` | O(n) |
| **Filter Recurring** | `Pet.get_recurring_tasks()` | Predicate filter: `frequency` field set | O(n) |
| **Conflict Detection** | `Scheduler.detect_conflicts_for_pet()` | Interval overlap: `task1.start < task2.end AND task2.start < task1.end` | O(n²) |
| **Get All Conflicts** | `Scheduler.get_all_conflicts()` | Apply conflict detection per pet | O(m·n²) |
| **Recurring Tasks** | `Task.get_next_occurrence()` | Generate next instance: `scheduled_at + timedelta(days=1 or 7)` | O(1) |

### Implementation Examples

**Sorting Example:**
```python
# Get today's tasks, sorted by priority (urgent first), then by time
scheduler = Scheduler(owner=my_owner)
today_tasks = scheduler.get_todays_schedule_by_priority()
# Returns: [high-priority tasks first, then medium, then low; within each group: sorted by time]
```

**Conflict Detection Example:**
```python
# Check if Mochi (cat) has any overlapping tasks
conflicts = scheduler.detect_conflicts_for_pet(mochi)
# Returns: [(feeding_task, walk_task), ...] if any tasks overlap
# Example: Feeding 2:00pm-2:15pm conflicts with Medication 2:10pm-2:20pm
```

**Recurring Task Example:**
```python
# Daily feeding task marks complete → next occurrence auto-generates
daily_feeding = Task(title="Feed Mochi", frequency="daily", scheduled_at=datetime(2026, 7, 11, 8, 0))
next_feeding = daily_feeding.get_next_occurrence()
# Returns: New Task with scheduled_at=datetime(2026, 7, 12, 8, 0) and parent_recurring_id tracking
```

### Tradeoffs

**Exact Interval Overlap vs. Buffer-Aware Scheduling:**
- Current: Exact overlap detection (catches conflicts down to 1 minute)
- Not Implemented: Buffer-aware warnings (e.g., flag if tasks within 5 min)
- Rationale: Pet care tasks typically space far apart; exact detection is simpler, transparent, and more Pythonic

---
## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
