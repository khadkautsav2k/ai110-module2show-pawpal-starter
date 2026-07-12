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


if __name__ == "__main__":
	pytest.main([__file__, "-v"])
