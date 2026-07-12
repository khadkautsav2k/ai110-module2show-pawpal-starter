"""
Test suite for PawPal pet care system.
Tests core functionality of Pet, Task, PetFood, and Owner classes.
"""

import pytest
from datetime import datetime, timedelta
from pawpal_system import Pet, Task, PetFood, Owner, Scheduler, TimelyCare


class TestTaskCompletion:
	"""Test Task completion functionality."""

	def test_task_completion_changes_status(self):
		"""Verify that calling complete() changes the task's status to completed."""
		# Arrange
		task = Task(title="Feed dog", description="Give kibble", completed=False)
		assert task.completed is False
		
		# Act
		task.complete()
		
		# Assert
		assert task.completed is True

	def test_task_completion_sets_timestamp(self):
		"""Verify that complete() sets the completed_at timestamp."""
		# Arrange
		task = Task(title="Feed dog", description="Give kibble")
		assert task.completed_at is None
		
		# Act
		before = datetime.now()
		task.complete()
		after = datetime.now()
		
		# Assert
		assert task.completed_at is not None
		assert before <= task.completed_at <= after

	def test_multiple_completions(self):
		"""Verify that complete() can be called multiple times without errors."""
		# Arrange
		task = Task(title="Clean bowl")
		
		# Act & Assert
		task.complete()
		assert task.completed is True
		first_time = task.completed_at
		
		task.complete()
		assert task.completed is True
		# Second completion updates the timestamp
		assert task.completed_at >= first_time


class TestTaskAddition:
	"""Test Task addition to Pet functionality."""

	def test_adding_task_to_pet_increases_count(self):
		"""Verify that adding a task to a Pet increases that pet's task count."""
		# Arrange
		pet = Pet(name="Buddy", species="Dog")
		assert len(pet.tasks) == 0
		
		# Act
		task = Task(title="Feed Buddy")
		pet.add_task(task)
		
		# Assert
		assert len(pet.tasks) == 1

	def test_adding_multiple_tasks_to_pet(self):
		"""Verify that multiple tasks can be added to a Pet."""
		# Arrange
		pet = Pet(name="Whiskers", species="Cat")
		task1 = Task(title="Feed")
		task2 = Task(title="Play")
		task3 = Task(title="Groom")
		
		# Act
		pet.add_task(task1)
		pet.add_task(task2)
		pet.add_task(task3)
		
		# Assert
		assert len(pet.tasks) == 3
		assert task1 in pet.tasks
		assert task2 in pet.tasks
		assert task3 in pet.tasks

	def test_added_task_is_in_pet_tasks_list(self):
		"""Verify that the added task is actually in the pet's tasks list."""
		# Arrange
		pet = Pet(name="Max", species="Dog")
		task = Task(title="Walk", description="30 min walk")
		
		# Act
		pet.add_task(task)
		
		# Assert
		assert task in pet.tasks


class TestPetFood:
	"""Test PetFood functionality."""

	def test_food_consumption(self):
		"""Verify that consume() decreases quantity."""
		# Arrange
		food = PetFood(brand="DogChow", type="Dry", quantity=10)
		
		# Act
		food.consume(3)
		
		# Assert
		assert food.quantity == 7

	def test_food_consumption_does_not_go_negative(self):
		"""Verify that consuming more than available quantity doesn't go negative."""
		# Arrange
		food = PetFood(brand="Kibble", type="Dry", quantity=2)
		
		# Act
		food.consume(5)
		
		# Assert
		assert food.quantity == 0

	def test_needs_refill_threshold(self):
		"""Verify that needs_refill() returns True when below threshold."""
		# Arrange
		food_low = PetFood(brand="Brand", type="Dry", quantity=1)
		food_ok = PetFood(brand="Brand", type="Dry", quantity=5)
		
		# Assert
		assert food_low.needs_refill(threshold=2) is True
		assert food_ok.needs_refill(threshold=2) is False

	def test_food_refill(self):
		"""Verify that refill() increases quantity."""
		# Arrange
		food = PetFood(brand="Brand", type="Dry", quantity=2)
		
		# Act
		food.refill(5)
		
		# Assert
		assert food.quantity == 7


class TestOwnerAndPets:
	"""Test Owner and Pet collection management."""

	def test_adding_pet_to_owner(self):
		"""Verify that adding a pet to owner increases pet count."""
		# Arrange
		owner = Owner(name="Alice")
		assert len(owner.pets) == 0
		
		# Act
		pet = Pet(name="Mochi", species="Cat")
		owner.add_pet(pet)
		
		# Assert
		assert len(owner.pets) == 1

	def test_owner_get_all_tasks(self):
		"""Verify that owner can retrieve all tasks from all pets."""
		# Arrange
		owner = Owner(name="Bob")
		pet1 = Pet(name="Dog1")
		pet2 = Pet(name="Cat1")
		
		task1 = Task(title="Feed Dog1")
		task2 = Task(title="Feed Cat1")
		task3 = Task(title="Walk Dog1")
		
		pet1.add_task(task1)
		pet1.add_task(task3)
		pet2.add_task(task2)
		
		owner.add_pet(pet1)
		owner.add_pet(pet2)
		
		# Act
		all_tasks = owner.get_all_tasks()
		
		# Assert
		assert len(all_tasks) == 3
		assert task1 in all_tasks
		assert task2 in all_tasks
		assert task3 in all_tasks

	def test_owner_get_pending_tasks(self):
		"""Verify that owner can retrieve only pending (incomplete) tasks."""
		# Arrange
		owner = Owner(name="Charlie")
		pet = Pet(name="Buddy")
		
		task1 = Task(title="Feed", completed=False)
		task2 = Task(title="Play", completed=True)
		task3 = Task(title="Walk", completed=False)
		
		pet.add_task(task1)
		pet.add_task(task2)
		pet.add_task(task3)
		owner.add_pet(pet)
		
		# Act
		pending = owner.get_all_pending_tasks()
		
		# Assert
		assert len(pending) == 2
		assert task1 in pending
		assert task3 in pending
		assert task2 not in pending


class TestScheduler:
	"""Test Scheduler functionality."""

	def test_scheduler_get_todays_schedule(self):
		"""Verify that Scheduler retrieves tasks scheduled for today."""
		# Arrange
		owner = Owner(name="Dana")
		pet = Pet(name="Pets")
		
		now = datetime.now()
		today_task = Task(title="Today", scheduled_at=now)
		tomorrow_task = Task(title="Tomorrow", scheduled_at=now + timedelta(days=1))
		
		pet.add_task(today_task)
		pet.add_task(tomorrow_task)
		owner.add_pet(pet)
		
		scheduler = Scheduler(owner=owner)
		
		# Act
		schedule = scheduler.get_todays_schedule()
		
		# Assert
		assert len(schedule) == 1
		assert today_task in schedule
		assert tomorrow_task not in schedule

	def test_scheduler_pending_tasks(self):
		"""Verify that Scheduler returns only pending tasks."""
		# Arrange
		owner = Owner(name="Eve")
		pet = Pet(name="Pet")
		
		task1 = Task(title="Pending", completed=False)
		task2 = Task(title="Done", completed=True)
		
		pet.add_task(task1)
		pet.add_task(task2)
		owner.add_pet(pet)
		
		scheduler = Scheduler(owner=owner)
		
		# Act
		pending = scheduler.get_pending_tasks()
		
		# Assert
		assert len(pending) == 1
		assert task1 in pending
		assert task2 not in pending


class TestTimelyCare:
	"""Test TimelyCare reminder functionality."""

	def test_timely_care_trigger_reminder(self):
		"""Verify that trigger_reminder() sets reminder_sent to True."""
		# Arrange
		care = TimelyCare(task_id="123", pet_id="456")
		assert care.reminder_sent is False
		
		# Act
		care.trigger_reminder()
		
		# Assert
		assert care.reminder_sent is True

	def test_timely_care_cancel(self):
		"""Verify that cancel() clears the scheduled_at time."""
		# Arrange
		now = datetime.now()
		care = TimelyCare(task_id="123", pet_id="456", scheduled_at=now)
		assert care.scheduled_at is not None
		
		# Act
		care.cancel()
		
		# Assert
		assert care.scheduled_at is None

	def test_timely_care_is_overdue(self):
		"""Verify that is_overdue() correctly identifies past times."""
		# Arrange
		past = datetime.now() - timedelta(hours=1)
		future = datetime.now() + timedelta(hours=1)
		
		care_past = TimelyCare(task_id="1", pet_id="1", scheduled_at=past)
		care_future = TimelyCare(task_id="2", pet_id="2", scheduled_at=future)
		
		# Assert
		assert care_past.is_overdue() is True
		assert care_future.is_overdue() is False


class TestSortingCorrectness:
	"""Test sorting algorithms for chronological and priority ordering."""

	def test_sort_by_time_empty_pet(self):
		"""Verify sorting an empty pet returns empty list without error."""
		# Arrange
		pet = Pet(name="Mochi", species="Cat")
		
		# Act
		result = pet.get_tasks_sorted_by_time()
		
		# Assert
		assert result == []
		assert isinstance(result, list)

	def test_sort_by_time_chronological_order(self):
		"""Verify tasks are sorted chronologically by scheduled_at (earliest first)."""
		# Arrange
		pet = Pet(name="Biscuit", species="Dog")
		now = datetime.now()
		
		task_2pm = Task(title="Walk", scheduled_at=now + timedelta(hours=2))
		task_1pm = Task(title="Feed", scheduled_at=now + timedelta(hours=1))
		task_3pm = Task(title="Play", scheduled_at=now + timedelta(hours=3))
		
		# Add in random order
		pet.add_task(task_3pm)
		pet.add_task(task_1pm)
		pet.add_task(task_2pm)
		
		# Act
		sorted_tasks = pet.get_tasks_sorted_by_time()
		
		# Assert
		assert sorted_tasks[0] == task_1pm  # 1pm first
		assert sorted_tasks[1] == task_2pm  # 2pm second
		assert sorted_tasks[2] == task_3pm  # 3pm last

	def test_sort_by_time_unscheduled_tasks_at_end(self):
		"""Verify tasks with None scheduled_at appear at end after scheduled tasks."""
		# Arrange
		pet = Pet(name="Luna", species="Cat")
		now = datetime.now()
		
		scheduled = Task(title="Scheduled", scheduled_at=now)
		unscheduled = Task(title="Unscheduled", scheduled_at=None)
		
		pet.add_task(unscheduled)
		pet.add_task(scheduled)
		
		# Act
		sorted_tasks = pet.get_tasks_sorted_by_time()
		
		# Assert
		assert sorted_tasks[0] == scheduled
		assert sorted_tasks[1] == unscheduled

	def test_sort_by_time_single_task(self):
		"""Verify sorting a single task returns list with that one task."""
		# Arrange
		pet = Pet(name="Spot", species="Dog")
		task = Task(title="Single", scheduled_at=datetime.now())
		pet.add_task(task)
		
		# Act
		sorted_tasks = pet.get_tasks_sorted_by_time()
		
		# Assert
		assert len(sorted_tasks) == 1
		assert sorted_tasks[0] == task

	def test_sort_by_time_same_scheduled_time(self):
		"""Verify tasks at exact same time are returned without error (stable sort)."""
		# Arrange
		pet = Pet(name="Max", species="Dog")
		same_time = datetime.now()
		
		task1 = Task(title="Task 1", scheduled_at=same_time)
		task2 = Task(title="Task 2", scheduled_at=same_time)
		task3 = Task(title="Task 3", scheduled_at=same_time)
		
		pet.add_task(task1)
		pet.add_task(task2)
		pet.add_task(task3)
		
		# Act
		sorted_tasks = pet.get_tasks_sorted_by_time()
		
		# Assert
		assert len(sorted_tasks) == 3
		assert all(t in sorted_tasks for t in [task1, task2, task3])

	def test_sort_by_priority_high_first(self):
		"""Verify high-priority tasks come before medium/low priority."""
		# Arrange
		pet = Pet(name="Fluffy", species="Cat")
		now = datetime.now()
		
		low = Task(title="Low", priority="low", scheduled_at=now)
		high = Task(title="High", priority="high", scheduled_at=now)
		medium = Task(title="Medium", priority="medium", scheduled_at=now)
		
		# Add in mixed order
		pet.add_task(medium)
		pet.add_task(low)
		pet.add_task(high)
		
		# Act
		sorted_tasks = pet.get_tasks_sorted_by_priority()
		
		# Assert
		assert sorted_tasks[0] == high
		assert sorted_tasks[1] == medium
		assert sorted_tasks[2] == low

	def test_sort_by_priority_then_time(self):
		"""Verify tasks sorted by priority first, then by time within same priority."""
		# Arrange
		pet = Pet(name="Buddy", species="Dog")
		now = datetime.now()
		
		# Same priority, different times
		high_2pm = Task(title="High 2pm", priority="high", scheduled_at=now + timedelta(hours=2))
		high_1pm = Task(title="High 1pm", priority="high", scheduled_at=now + timedelta(hours=1))
		low_3pm = Task(title="Low 3pm", priority="low", scheduled_at=now + timedelta(hours=3))
		
		pet.add_task(high_2pm)
		pet.add_task(low_3pm)
		pet.add_task(high_1pm)
		
		# Act
		sorted_tasks = pet.get_tasks_sorted_by_priority()
		
		# Assert - high priority tasks first, ordered by time
		assert sorted_tasks[0] == high_1pm  # High, earliest
		assert sorted_tasks[1] == high_2pm  # High, later
		assert sorted_tasks[2] == low_3pm   # Low

	def test_sort_by_priority_unknown_priority(self):
		"""Verify tasks with unknown priority are treated as low priority."""
		# Arrange
		pet = Pet(name="Rex", species="Dog")
		now = datetime.now()
		
		high = Task(title="High", priority="high", scheduled_at=now)
		unknown = Task(title="Unknown", priority="unknown", scheduled_at=now)
		medium = Task(title="Medium", priority="medium", scheduled_at=now)
		
		pet.add_task(unknown)
		pet.add_task(high)
		pet.add_task(medium)
		
		# Act
		sorted_tasks = pet.get_tasks_sorted_by_priority()
		
		# Assert
		assert sorted_tasks[0] == high
		assert sorted_tasks[1] == medium
		assert sorted_tasks[2] == unknown  # Unknown treated as lowest

	def test_owner_sort_all_tasks_by_time(self):
		"""Verify Owner can sort all tasks across all pets chronologically."""
		# Arrange
		owner = Owner(name="Owner1")
		pet1 = Pet(name="Pet1")
		pet2 = Pet(name="Pet2")
		
		now = datetime.now()
		task1_2pm = Task(title="Pet1 2pm", scheduled_at=now + timedelta(hours=2))
		task1_1pm = Task(title="Pet1 1pm", scheduled_at=now + timedelta(hours=1))
		task2_3pm = Task(title="Pet2 3pm", scheduled_at=now + timedelta(hours=3))
		
		pet1.add_task(task1_2pm)
		pet1.add_task(task1_1pm)
		pet2.add_task(task2_3pm)
		
		owner.add_pet(pet1)
		owner.add_pet(pet2)
		
		# Act
		sorted_tasks = owner.get_all_tasks_sorted_by_time()
		
		# Assert
		assert sorted_tasks[0] == task1_1pm
		assert sorted_tasks[1] == task1_2pm
		assert sorted_tasks[2] == task2_3pm

	def test_scheduler_get_todays_schedule_by_priority(self):
		"""Verify Scheduler returns today's tasks sorted by priority then time."""
		# Arrange
		owner = Owner(name="Owner2")
		pet = Pet(name="Pet")
		
		now = datetime.now()
		today_high = Task(title="High", priority="high", scheduled_at=now)
		today_low_early = Task(title="Low Early", priority="low", scheduled_at=now + timedelta(hours=1))
		tomorrow = Task(title="Tomorrow", scheduled_at=now + timedelta(days=1))
		
		pet.add_task(today_low_early)
		pet.add_task(tomorrow)
		pet.add_task(today_high)
		
		owner.add_pet(pet)
		scheduler = Scheduler(owner=owner)
		
		# Act
		schedule = scheduler.get_todays_schedule_by_priority()
		
		# Assert
		assert len(schedule) == 2  # Only today's tasks
		assert schedule[0] == today_high  # High priority first
		assert schedule[1] == today_low_early


class TestRecurrenceLogic:
	"""Test recurring task generation and automation."""

	def test_daily_task_get_next_occurrence(self):
		"""Verify daily task generates next occurrence 24 hours later."""
		# Arrange
		scheduled = datetime(2026, 7, 12, 8, 0)  # July 12, 8:00 AM
		task = Task(
			title="Daily Feeding",
			frequency="daily",
			priority="high",
			duration_minutes=10,
			scheduled_at=scheduled
		)
		
		# Act
		next_task = task.get_next_occurrence()
		
		# Assert
		assert next_task is not None
		assert next_task.scheduled_at == datetime(2026, 7, 13, 8, 0)  # July 13, 8:00 AM
		assert next_task.title == "Daily Feeding"
		assert next_task.priority == "high"
		assert next_task.duration_minutes == 10
		assert next_task.frequency == "daily"

	def test_weekly_task_get_next_occurrence(self):
		"""Verify weekly task generates next occurrence 7 days later."""
		# Arrange
		scheduled = datetime(2026, 7, 12, 14, 0)  # July 12 (Sunday), 2:00 PM
		task = Task(
			title="Weekly Grooming",
			frequency="weekly",
			priority="medium",
			scheduled_at=scheduled
		)
		
		# Act
		next_task = task.get_next_occurrence()
		
		# Assert
		assert next_task is not None
		assert next_task.scheduled_at == datetime(2026, 7, 19, 14, 0)  # July 19 (next Sunday), 2:00 PM
		assert next_task.title == "Weekly Grooming"
		assert next_task.frequency == "weekly"

	def test_non_recurring_task_returns_none(self):
		"""Verify non-recurring task (frequency=None) returns None."""
		# Arrange
		task = Task(
			title="One-time task",
			frequency=None,
			scheduled_at=datetime.now()
		)
		
		# Act
		next_task = task.get_next_occurrence()
		
		# Assert
		assert next_task is None

	def test_unscheduled_recurring_task_returns_none(self):
		"""Verify recurring task with no scheduled_at returns None."""
		# Arrange
		task = Task(
			title="Recurring but unscheduled",
			frequency="daily",
			scheduled_at=None
		)
		
		# Act
		next_task = task.get_next_occurrence()
		
		# Assert
		assert next_task is None

	def test_unknown_frequency_returns_none(self):
		"""Verify unknown frequency string returns None without error."""
		# Arrange
		task = Task(
			title="Unknown frequency",
			frequency="monthly",  # Not supported
			scheduled_at=datetime.now()
		)
		
		# Act
		next_task = task.get_next_occurrence()
		
		# Assert
		assert next_task is None

	def test_recurring_task_has_unique_id(self):
		"""Verify generated recurring task has different ID from parent."""
		# Arrange
		task = Task(
			title="Daily",
			frequency="daily",
			scheduled_at=datetime.now()
		)
		parent_id = task.id
		
		# Act
		next_task = task.get_next_occurrence()
		
		# Assert
		assert next_task is not None
		assert next_task.id != parent_id  # New ID
		assert len(next_task.id) > 0

	def test_recurring_task_tracks_parent(self):
		"""Verify generated task has parent_recurring_id pointing to original."""
		# Arrange
		task = Task(
			title="Daily Task",
			frequency="daily",
			scheduled_at=datetime.now()
		)
		
		# Act
		next_task = task.get_next_occurrence()
		
		# Assert
		assert next_task is not None
		assert next_task.parent_recurring_id == task.id

	def test_recurring_task_second_generation_tracks_original(self):
		"""Verify second-generation recurring task still tracks the original parent."""
		# Arrange
		original = Task(
			title="Original",
			frequency="daily",
			scheduled_at=datetime(2026, 7, 12, 8, 0)
		)
		original_id = original.id
		
		# Act
		first_next = original.get_next_occurrence()
		second_next = first_next.get_next_occurrence()
		
		# Assert
		assert first_next is not None
		assert second_next is not None
		assert first_next.parent_recurring_id == original_id
		assert second_next.parent_recurring_id == original_id  # Still tracks original

	def test_pet_get_recurring_tasks(self):
		"""Verify Pet can filter and return only recurring tasks."""
		# Arrange
		pet = Pet(name="Repeater", species="Dog")
		
		daily_task = Task(title="Daily", frequency="daily", scheduled_at=datetime.now())
		weekly_task = Task(title="Weekly", frequency="weekly", scheduled_at=datetime.now())
		one_time = Task(title="One-time", frequency=None, scheduled_at=datetime.now())
		
		pet.add_task(daily_task)
		pet.add_task(one_time)
		pet.add_task(weekly_task)
		
		# Act
		recurring = pet.get_recurring_tasks()
		
		# Assert
		assert len(recurring) == 2
		assert daily_task in recurring
		assert weekly_task in recurring
		assert one_time not in recurring


class TestConflictDetection:
	"""Test conflict detection for overlapping tasks."""

	def test_detect_conflicts_empty_pet(self):
		"""Verify empty pet with no tasks has no conflicts."""
		# Arrange
		owner = Owner(name="Owner")
		pet = Pet(name="Pet")
		owner.add_pet(pet)
		scheduler = Scheduler(owner=owner)
		
		# Act
		conflicts = scheduler.detect_conflicts_for_pet(pet)
		
		# Assert
		assert conflicts == []

	def test_detect_conflicts_single_task(self):
		"""Verify single task cannot conflict with itself; returns empty list."""
		# Arrange
		owner = Owner(name="Owner")
		pet = Pet(name="Pet")
		
		task = Task(
			title="Single",
			scheduled_at=datetime(2026, 7, 12, 10, 0),
			duration_minutes=30
		)
		pet.add_task(task)
		owner.add_pet(pet)
		scheduler = Scheduler(owner=owner)
		
		# Act
		conflicts = scheduler.detect_conflicts_for_pet(pet)
		
		# Assert
		assert conflicts == []

	def test_detect_conflicts_overlapping_tasks(self):
		"""Verify overlapping tasks are detected as conflicts."""
		# Arrange
		owner = Owner(name="Owner")
		pet = Pet(name="Pet")
		
		# Task 1: 10:00 - 10:30
		task1 = Task(
			title="Feed",
			scheduled_at=datetime(2026, 7, 12, 10, 0),
			duration_minutes=30
		)
		# Task 2: 10:15 - 10:45 (overlaps with task1)
		task2 = Task(
			title="Med",
			scheduled_at=datetime(2026, 7, 12, 10, 15),
			duration_minutes=30
		)
		
		pet.add_task(task1)
		pet.add_task(task2)
		owner.add_pet(pet)
		scheduler = Scheduler(owner=owner)
		
		# Act
		conflicts = scheduler.detect_conflicts_for_pet(pet)
		
		# Assert
		assert len(conflicts) == 1
		assert (task1, task2) in conflicts or (task2, task1) in conflicts

	def test_detect_conflicts_back_to_back_no_conflict(self):
		"""Verify back-to-back tasks (end=start) do NOT conflict."""
		# Arrange
		owner = Owner(name="Owner")
		pet = Pet(name="Pet")
		
		# Task 1: 10:00 - 10:15
		task1 = Task(
			title="Feed",
			scheduled_at=datetime(2026, 7, 12, 10, 0),
			duration_minutes=15
		)
		# Task 2: 10:15 - 10:30 (starts exactly when task1 ends)
		task2 = Task(
			title="Walk",
			scheduled_at=datetime(2026, 7, 12, 10, 15),
			duration_minutes=15
		)
		
		pet.add_task(task1)
		pet.add_task(task2)
		owner.add_pet(pet)
		scheduler = Scheduler(owner=owner)
		
		# Act
		conflicts = scheduler.detect_conflicts_for_pet(pet)
		
		# Assert
		assert conflicts == []  # No conflict (sequential, not overlapping)

	def test_detect_conflicts_three_overlapping_tasks(self):
		"""Verify three overlapping tasks detect all three pair conflicts."""
		# Arrange
		owner = Owner(name="Owner")
		pet = Pet(name="Pet")
		
		# All three tasks overlap in the same time window
		task1 = Task(
			title="Task1",
			scheduled_at=datetime(2026, 7, 12, 10, 0),
			duration_minutes=60
		)
		task2 = Task(
			title="Task2",
			scheduled_at=datetime(2026, 7, 12, 10, 30),
			duration_minutes=60
		)
		task3 = Task(
			title="Task3",
			scheduled_at=datetime(2026, 7, 12, 11, 0),
			duration_minutes=30
		)
		
		pet.add_task(task1)
		pet.add_task(task2)
		pet.add_task(task3)
		owner.add_pet(pet)
		scheduler = Scheduler(owner=owner)
		
		# Act
		conflicts = scheduler.detect_conflicts_for_pet(pet)
		
		# Assert
		assert len(conflicts) == 2  # (1,2), (2,3); task1 ends 11:00 == task3 start, adjacent not overlapping

	def test_detect_conflicts_tasks_with_no_duration(self):
		"""Verify tasks with 0 duration_minutes are filtered out (no conflicts)."""
		# Arrange
		owner = Owner(name="Owner")
		pet = Pet(name="Pet")
		
		task1 = Task(
			title="Scheduled",
			scheduled_at=datetime(2026, 7, 12, 10, 0),
			duration_minutes=30
		)
		task2 = Task(
			title="No duration",
			scheduled_at=datetime(2026, 7, 12, 10, 15),
			duration_minutes=0  # No duration
		)
		
		pet.add_task(task1)
		pet.add_task(task2)
		owner.add_pet(pet)
		scheduler = Scheduler(owner=owner)
		
		# Act
		conflicts = scheduler.detect_conflicts_for_pet(pet)
		
		# Assert
		assert conflicts == []  # task2 filtered out, no conflicts

	def test_detect_conflicts_unscheduled_tasks(self):
		"""Verify tasks with None scheduled_at are filtered out (no conflicts)."""
		# Arrange
		owner = Owner(name="Owner")
		pet = Pet(name="Pet")
		
		task1 = Task(
			title="Scheduled",
			scheduled_at=datetime(2026, 7, 12, 10, 0),
			duration_minutes=30
		)
		task2 = Task(
			title="Unscheduled",
			scheduled_at=None,
			duration_minutes=30
		)
		
		pet.add_task(task1)
		pet.add_task(task2)
		owner.add_pet(pet)
		scheduler = Scheduler(owner=owner)
		
		# Act
		conflicts = scheduler.detect_conflicts_for_pet(pet)
		
		# Assert
		assert conflicts == []  # task2 filtered out, no conflicts

	def test_get_all_conflicts_multiple_pets(self):
		"""Verify Scheduler can detect conflicts across multiple pets."""
		# Arrange
		owner = Owner(name="Owner")
		pet1 = Pet(name="Pet1")
		pet2 = Pet(name="Pet2")
		
		# Pet1 has conflicting tasks
		pet1_task1 = Task(
			title="Pet1 Task1",
			scheduled_at=datetime(2026, 7, 12, 10, 0),
			duration_minutes=30
		)
		pet1_task2 = Task(
			title="Pet1 Task2",
			scheduled_at=datetime(2026, 7, 12, 10, 15),
			duration_minutes=30
		)
		
		# Pet2 has no conflicts
		pet2_task1 = Task(
			title="Pet2 Task1",
			scheduled_at=datetime(2026, 7, 12, 10, 0),
			duration_minutes=30
		)
		
		pet1.add_task(pet1_task1)
		pet1.add_task(pet1_task2)
		pet2.add_task(pet2_task1)
		
		owner.add_pet(pet1)
		owner.add_pet(pet2)
		scheduler = Scheduler(owner=owner)
		
		# Act
		all_conflicts = scheduler.get_all_conflicts()
		
		# Assert
		assert pet1 in all_conflicts  # Pet1 has conflicts
		assert pet2 not in all_conflicts  # Pet2 has no conflicts
		assert len(all_conflicts[pet1]) == 1  # One conflict pair


if __name__ == "__main__":
	pytest.main([__file__, "-v"])
