from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
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

	def complete(self) -> None:
		"""Mark task as completed and record the completion timestamp."""
		self.completed = True
		self.completed_at = datetime.now()

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

