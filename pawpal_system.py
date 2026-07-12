from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import uuid


def _id() -> str:
	"""Generate a unique UUID string identifier."""
	return str(uuid.uuid4())


@dataclass
class Pet:
	id: str = field(default_factory=_id)
	name: str = ""
	species: str = ""
	age: int = 0
	foods: List["PetFood"] = field(default_factory=list)
	tasks: List["Task"] = field(default_factory=list)

	def profile(self) -> dict:
		"""Return a dictionary of the pet's profile information."""
		return {"id": self.id, "name": self.name, "species": self.species, "age": self.age}

	def add_food(self, food: "PetFood") -> None:
		"""Add a food item to the pet's inventory."""
		self.foods.append(food)

	def add_task(self, task: "Task") -> None:
		"""Add a task to the pet's task list."""
		self.tasks.append(task)

	def get_pending_tasks(self) -> List["Task"]:
		"""Return all incomplete tasks for this pet."""
		return [t for t in self.tasks if not t.completed]

	def get_low_stock_foods(self, threshold: int = 2) -> List["PetFood"]:
		"""Return foods with quantity at or below the threshold."""
		return [f for f in self.foods if f.quantity <= threshold]

	def get_tasks_sorted_by_time(self) -> List["Task"]:
		"""
		Sort pet's tasks chronologically by scheduled_at timestamp.
		
		Algorithm: O(n log n) comparison sort using Python's built-in sorted().
		- Tasks with None scheduled_at are placed at end (using datetime.max as fallback)
		- Sorting key: (scheduled_at timestamp)
		- Use case: Display tasks in order of occurrence for day/week planning
		
		Returns:
			List of Task objects sorted earliest to latest by scheduled_at.
		"""
		return sorted(self.tasks, key=lambda t: t.scheduled_at or datetime.max)

	def get_tasks_sorted_by_priority(self) -> List["Task"]:
		"""
		Sort pet's tasks by priority level, then chronologically by time.
		
		Algorithm: O(n log n) multi-key sort using tuple-based sorting.
		- Primary key: priority rank (high=0, medium=1, low=2)
		- Secondary key: scheduled_at timestamp (for deterministic ordering within priority)
		- Unknown priorities treated as low (rank=3)
		- Use case: Triage tasks when multiple must be done; do high-priority first
		
		Returns:
			List of Task objects sorted by priority (urgent first), then by time.
		"""
		priority_order = {"high": 0, "medium": 1, "low": 2}
		return sorted(self.tasks, 
			key=lambda t: (priority_order.get(t.priority, 3), t.scheduled_at or datetime.max))

	def get_tasks_by_status(self, completed: bool = False) -> List["Task"]:
		"""
		Filter pet's tasks by completion status using simple predicate matching.
		
		Algorithm: O(n) linear filter using list comprehension.
		- Iterates through all tasks checking completed boolean flag
		- Use case: Separate done vs pending work; show completed history
		
		Args:
			completed: If True, return completed tasks; if False, return pending tasks.
		
		Returns:
			List of Task objects matching the completion status.
		"""
		return [t for t in self.tasks if t.completed == completed]

	def get_high_priority_tasks(self) -> List["Task"]:
		"""
		Filter tasks to extract only high-priority items for urgent attention.
		
		 Algorithm: O(n) single-pass filter on priority field.
		- Predicate: task.priority == "high"
		- Use case: Quick lookup for urgent/critical care (medication, emergency)
		
		Returns:
			List of Task objects with priority="high".
		"""
		return [t for t in self.tasks if t.priority == "high"]

	def get_recurring_tasks(self) -> List["Task"]:
		"""
		Filter tasks to extract recurring items (daily/weekly automation).
		
		Algorithm: O(n) filter on frequency field presence.
		- Predicate: task.frequency is not None/empty
		- Frequencies: "daily" (repeat every 24h), "weekly" (repeat every 7d)
		- Use case: Identify tasks that auto-generate next occurrence on completion
		
		Returns:
			List of Task objects with frequency set (recurring).
		"""
		return [t for t in self.tasks if t.frequency]


@dataclass
class PetFood:
	id: str = field(default_factory=_id)
	brand: str = ""
	type: str = ""
	quantity: int = 0

	def consume(self, amount: int = 1) -> None:
		"""Decrease food quantity by amount consumed, preventing negative values."""
		self.quantity = max(0, self.quantity - amount)

	def refill(self, amount: int) -> None:
		"""Increase food quantity by the refill amount."""
		self.quantity += amount

	def needs_refill(self, threshold: int = 2) -> bool:
		"""Return True if quantity is at or below the refill threshold."""
		return self.quantity <= threshold


@dataclass
class Task:
	id: str = field(default_factory=_id)
	title: str = ""
	description: str = ""
	completed: bool = False
	scheduled_at: Optional[datetime] = None
	completed_at: Optional[datetime] = None
	priority: str = "medium"  # "high", "medium", "low"
	duration_minutes: int = 15  # Estimated duration
	frequency: Optional[str] = None  # "daily", "weekly", or None
	parent_recurring_id: Optional[str] = None  # ID of recurring task parent

	def complete(self) -> None:
		"""Mark task as completed and record the completion timestamp."""
		self.completed = True
		self.completed_at = datetime.now()

	def get_next_occurrence(self) -> Optional["Task"]:
		"""
		Generate the next occurrence of a recurring task for automation scheduling.
		
		Algorithm: O(1) date calculation and Task instantiation.
		- Calculates next scheduled time using timedelta(days=1) for daily or timedelta(days=7) for weekly
		- Creates new Task instance with identical properties but new ID and future scheduled_at
		- Chains occurrences using parent_recurring_id to track lineage
		
		Use case: When a recurring task is marked complete(), scheduler auto-adds the next instance.
		Example: Daily feeding at 8am → upon completion, new feeding task created for 8am next day.
		
		Returns:
			New Task instance for next occurrence, or None if not recurring or unscheduled.
		"""
		if not self.frequency or not self.scheduled_at:
			return None
		
		# Calculate next scheduled time based on frequency
		if self.frequency == "daily":
			next_time = self.scheduled_at + timedelta(days=1)
		elif self.frequency == "weekly":
			next_time = self.scheduled_at + timedelta(days=7)
		else:
			return None
		
		# Create new task instance with same properties but new ID
		next_task = Task(
			title=self.title,
			description=self.description,
			scheduled_at=next_time,
			priority=self.priority,
			duration_minutes=self.duration_minutes,
			frequency=self.frequency,
			parent_recurring_id=self.parent_recurring_id or self.id
		)
		return next_task

	def is_overdue(self) -> bool:
		"""Return True if task is incomplete and past its scheduled time."""
		if self.scheduled_at and not self.completed:
			return datetime.now() > self.scheduled_at
		return False


@dataclass
class TimelyCare:
	id: str = field(default_factory=_id)
	task_id: str = ""
	pet_id: str = ""
	scheduled_at: Optional[datetime] = field(default_factory=datetime.now)
	reminder_sent: bool = False
	task: Optional["Task"] = None
	pet: Optional["Pet"] = None

	def trigger_reminder(self) -> None:
		"""Mark the reminder as sent."""
		self.reminder_sent = True

	def cancel(self) -> None:
		"""Cancel the scheduled care by clearing the scheduled time."""
		self.scheduled_at = None

	def is_overdue(self) -> bool:
		"""Return True if the reminder is past its scheduled time."""
		if self.scheduled_at:
			return datetime.now() > self.scheduled_at
		return False


@dataclass
class Owner:
	id: str = field(default_factory=_id)
	name: str = ""
	pets: List["Pet"] = field(default_factory=list)

	def add_pet(self, pet: "Pet") -> None:
		"""Add a pet to the owner's collection."""
		self.pets.append(pet)

	def get_all_tasks(self) -> List["Task"]:
		"""Retrieve all tasks across all pets."""
		tasks = []
		for pet in self.pets:
			tasks.extend(pet.tasks)
		return tasks

	def get_all_pending_tasks(self) -> List["Task"]:
		"""Retrieve all incomplete tasks."""
		return [t for t in self.get_all_tasks() if not t.completed]

	def get_all_overdue_tasks(self) -> List["Task"]:
		"""Retrieve tasks that are past their scheduled time."""
		return [t for t in self.get_all_tasks() if t.is_overdue()]

	def get_tasks_for_pet(self, pet: "Pet") -> List["Task"]:
		"""Get all tasks for a specific pet."""
		return pet.tasks

	def get_all_tasks_sorted_by_time(self) -> List["Task"]:
		"""Get all tasks across all pets, sorted by scheduled time."""
		all_tasks = self.get_all_tasks()
		return sorted(all_tasks, key=lambda t: t.scheduled_at or datetime.max)

	def get_all_tasks_sorted_by_priority(self) -> List["Task"]:
		"""Get all tasks across all pets, sorted by priority then time."""
		all_tasks = self.get_all_tasks()
		priority_order = {"high": 0, "medium": 1, "low": 2}
		return sorted(all_tasks,
			key=lambda t: (priority_order.get(t.priority, 3), t.scheduled_at or datetime.max))

	def get_high_priority_tasks(self) -> List["Task"]:
		"""Get all high-priority tasks across all pets."""
		return [t for t in self.get_all_tasks() if t.priority == "high"]

	def get_recurring_tasks(self) -> List["Task"]:
		"""Get all recurring tasks (daily/weekly) across all pets."""
		return [t for t in self.get_all_tasks() if t.frequency]

	def get_all_tasks_sorted_by_time(self) -> List["Task"]:
		"""
		Aggregate and sort all tasks across all pets chronologically.
		
		Algorithm: O(m log m) where m = total tasks (aggregation O(m) + sort O(m log m)).
		- Collects tasks from all owner.pets
		- Sorts by scheduled_at timestamp (earliest first)
		- Unscheduled tasks (None) placed at end
		- Use case: Multi-pet household needs unified day/week view
		
		Returns:
			List of all Task objects across all pets, sorted chronologically.
		"""
		return sorted(self.get_all_tasks(), key=lambda t: t.scheduled_at or datetime.max)

	def get_all_tasks_sorted_by_priority(self) -> List["Task"]:
		"""
		Aggregate and sort all tasks across all pets by priority, then chronologically.
		
		Algorithm: O(m log m) multi-key sort across all m total tasks.
		- Primary key: priority rank (high=0, medium=1, low=2)
		- Secondary key: scheduled_at timestamp
		- Use case: Owner with multiple pets sees what's most urgent across all
		
		Returns:
			List of all Task objects sorted by priority (urgent first), then by time.
		"""
		priority_order = {"high": 0, "medium": 1, "low": 2}
		return sorted(self.get_all_tasks(), 
			key=lambda t: (priority_order.get(t.priority, 3), t.scheduled_at or datetime.max))

	def get_tasks_for_pet(self, pet: "Pet") -> List["Task"]:
		"""Get all tasks for a specific pet."""
		return pet.tasks

	def get_all_high_priority_tasks(self) -> List["Task"]:
		"""
		Filter all tasks across all pets to extract high-priority items only.
		
		Algorithm: O(m) single-pass filter where m = total tasks.
		- Aggregates all pet tasks, then filters by priority == "high"
		- Use case: Quick overview of critical care tasks across household
		
		Returns:
			List of high-priority Task objects from all pets.
		"""
		return [t for t in self.get_all_tasks() if t.priority == "high"]

	def get_all_pending_by_priority(self) -> List["Task"]:
		"""
		Filter incomplete tasks across all pets and sort by priority (urgent first).
		
		Algorithm: O(m) filter + O(n log n) sort where m=total, n=pending tasks.
		- Filters to incomplete tasks (completed=False)
		- Sorts filtered list by priority rank (high→medium→low)
		- Use case: Owner's todo list for today, organized by urgency
		
		Returns:
			List of incomplete Task objects sorted by priority.
		"""
		pending = self.get_all_pending_tasks()
		priority_order = {"high": 0, "medium": 1, "low": 2}
		return sorted(pending, key=lambda t: priority_order.get(t.priority, 3))


@dataclass
class Scheduler:
	owner: "Owner"

	def get_tasks_to_execute(self) -> List["Task"]:
		"""Return all pending, overdue tasks."""
		return self.owner.get_all_overdue_tasks()

	def get_pending_tasks(self) -> List["Task"]:
		"""Return all pending tasks (not yet completed)."""
		return self.owner.get_all_pending_tasks()

	def get_todays_schedule(self) -> List["Task"]:
		"""Return all tasks for today sorted by scheduled time."""
		today = datetime.now().date()
		tasks = [
			t for t in self.owner.get_all_tasks()
			if t.scheduled_at and t.scheduled_at.date() == today
		]
		return sorted(tasks, key=lambda t: t.scheduled_at)

	def get_todays_schedule_by_priority(self) -> List["Task"]:
		"""Return today's tasks sorted by priority then time."""
		today = datetime.now().date()
		tasks = [
			t for t in self.owner.get_all_tasks()
			if t.scheduled_at and t.scheduled_at.date() == today
		]
		priority_order = {"high": 0, "medium": 1, "low": 2}
		return sorted(tasks,
			key=lambda t: (priority_order.get(t.priority, 3), t.scheduled_at))

	def detect_conflicts_for_pet(self, pet: "Pet") -> List[Tuple['Task', 'Task']]:
		"""
		Detect scheduling conflicts (overlapping tasks) for a specific pet.
		
		Algorithm: O(n²) brute-force interval overlap detection with pre-filtering.
		- Pre-filter: Keep only tasks with both scheduled_at time AND duration_minutes set
		- Core check: For each pair (i, i+1..n), test interval overlap: 
		  task1.start < task2.end AND task2.start < task1.end
		- Use case: Warn owner when two pet tasks would collide (e.g., 2 walks at 2pm)
		- Complexity acceptable: O(n²) with small n (< 50 daily tasks typical)
		
		Args:
			pet: Pet object to check for scheduling conflicts.
		
		Returns:
			List of (Task, Task) tuples where tasks overlap in time.
		"""
		conflicts = []
		# Pre-filter and pre-calculate end times for efficiency
		tasks_with_times = [
			(t, t.scheduled_at + timedelta(minutes=t.duration_minutes))
			for t in pet.tasks 
			if t.scheduled_at and t.duration_minutes
		]
		
		# Check each pair for overlap - using tuple unpacking for clarity
		for i, (task1, end1) in enumerate(tasks_with_times):
			for task2, end2 in tasks_with_times[i+1:]:
				# Interval overlap: task1_start < task2_end AND task2_start < task1_end
				if task1.scheduled_at < end2 and task2.scheduled_at < end1:
					conflicts.append((task1, task2))
		
		return conflicts

	def get_all_conflicts(self) -> dict['Pet', List[Tuple['Task', 'Task']]]:
		"""
		Detect all scheduling conflicts across all pets in the owner's collection.
		
		Algorithm: O(m * n²) where m=pets, n=tasks/pet; calls detect_conflicts_for_pet() per pet.
		- Iterates through each pet in owner.pets
		- Detects conflicts for that pet
		- Only includes pets with at least one conflict in result dict
		- Use case: Dashboard showing all pets' scheduling problems at once
		
		Returns:
			Dict mapping Pet → List of conflicting (Task, Task) tuples.
			Empty dict {} if no conflicts found.
		"""
		conflicts_by_pet = {}
		for pet in self.owner.pets:
			conflicts = self.detect_conflicts_for_pet(pet)
			if conflicts:
				conflicts_by_pet[pet] = conflicts
		return conflicts_by_pet


__all__ = ["Pet", "PetFood", "Task", "TimelyCare", "Owner", "Scheduler"]


if __name__ == "__main__":
	# Small usage example
	pet = Pet(name="Mochi", species="Cat", age=2)
	food = PetFood(brand="HappyPaws", type="Dry", quantity=1)
	task = Task(title="Feed Mochi", description="Give 1 scoop of dry food", scheduled_at=datetime.now())
	timely_care = TimelyCare(task_id=task.id, pet_id=pet.id, task=task, pet=pet)

	pet.add_food(food)
	pet.add_task(task)

	print("Pet profile:", pet.profile())
	print("Pending tasks:", pet.get_pending_tasks())
	print("Low stock foods:", pet.get_low_stock_foods(threshold=2))
	print("Food needs refill?", food.needs_refill(threshold=2))
	print("Task overdue?", task.is_overdue())
	print("Care reminder overdue?", timely_care.is_overdue())
	
	# Complete the task and show timestamp
	task.complete()
	print("Task completed at:", task.completed_at)

