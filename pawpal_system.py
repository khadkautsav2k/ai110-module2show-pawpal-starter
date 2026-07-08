from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid


def _id() -> str:
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
		return {"id": self.id, "name": self.name, "species": self.species, "age": self.age}

	def add_food(self, food: "PetFood") -> None:
		self.foods.append(food)

	def add_task(self, task: "Task") -> None:
		self.tasks.append(task)


@dataclass
class PetFood:
	id: str = field(default_factory=_id)
	brand: str = ""
	type: str = ""
	quantity: int = 0

	def consume(self, amount: int = 1) -> None:
		self.quantity = max(0, self.quantity - amount)

	def refill(self, amount: int) -> None:
		self.quantity += amount


@dataclass
class Task:
	id: str = field(default_factory=_id)
	title: str = ""
	description: str = ""
	completed: bool = False
	scheduled_at: Optional[datetime] = None

	def complete(self) -> None:
		self.completed = True


@dataclass
class TimelyCare:
	id: str = field(default_factory=_id)
	task_id: str = ""
	pet_id: str = ""
	scheduled_at: Optional[datetime] = field(default_factory=datetime.now)
	reminder_sent: bool = False

	def trigger_reminder(self) -> None:
		self.reminder_sent = True

	def cancel(self) -> None:
		self.scheduled_at = None


__all__ = ["Pet", "PetFood", "Task", "TimelyCare"]


if __name__ == "__main__":
	# Small usage example
	pet = Pet(name="Mochi", species="Cat", age=2)
	food = PetFood(brand="HappyPaws", type="Dry", quantity=5)
	task = Task(title="Feed Mochi", description="Give 1 scoop of dry food", scheduled_at=datetime.now())

	pet.add_food(food)
	pet.add_task(task)

	print("Pet profile:", pet.profile())
	print("Foods:", [(f.brand, f.quantity) for f in pet.foods])
	print("Tasks:", [(t.title, t.completed) for t in pet.tasks])

