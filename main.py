#!/usr/bin/env python3
"""
PawPal Demo Script: Demonstrates the pet care system with Owner, Pets, Tasks, and Scheduler.
"""

from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, PetFood, Scheduler


def main():
	# Create an Owner
	owner = Owner(name="Alice")
	print(f"Created Owner: {owner.name}\n")

	# Create two Pets
	pet1 = Pet(name="Mochi", species="Cat", age=2)
	pet2 = Pet(name="Rex", species="Dog", age=5)
	owner.add_pet(pet1)
	owner.add_pet(pet2)
	print(f"Added pets: {pet1.name} ({pet1.species}) and {pet2.name} ({pet2.species})\n")

	# Create tasks with different times, deliberately out of order
	# This demonstrates sorting capabilities
	now = datetime.now()
	
	# Task 3: Clean bowls at 3 PM (latest)
	task3 = Task(
		title="Clean Rex's bowls",
		description="Wash and refill water and food bowls",
		scheduled_at=now + timedelta(hours=3),
		priority="high",
		duration_minutes=10
	)
	
	# Task 1: Feed Mochi at 1 PM (earliest) - Low priority
	task1 = Task(
		title="Feed Mochi",
		description="Give 1 scoop of dry food",
		scheduled_at=now + timedelta(hours=1),
		priority="low",
		duration_minutes=5
	)
	
	# Task 2: Play with Mochi at 2 PM (middle) - High priority
	task2 = Task(
		title="Play with Mochi",
		description="15 minutes of interactive play",
		scheduled_at=now + timedelta(hours=2),
		priority="high",
		duration_minutes=15
	)

	# Add tasks out of order (3, 1, 2) to test sorting
	pet1.add_task(task3)  # Added first but scheduled last
	pet1.add_task(task1)  # Added second but scheduled first
	pet2.add_task(task2)  # Added third, middle time
	print(f"Added 3 tasks OUT OF ORDER to test sorting:\n")

	# Add food to pets
	food1 = PetFood(brand="HappyPaws", type="Dry", quantity=5)
	food2 = PetFood(brand="DogDelight", type="Wet", quantity=2)
	pet1.add_food(food1)
	pet2.add_food(food2)

	# Create Scheduler and print Today's Schedule
	scheduler = Scheduler(owner=owner)
	
	print("=" * 60)
	print(f"TODAY'S SCHEDULE FOR {owner.name.upper()}")
	print("=" * 60)
	
	todays_tasks = scheduler.get_todays_schedule()
	
	if todays_tasks:
		for i, task in enumerate(todays_tasks, 1):
			# Find which pet owns this task
			pet_name = next((p.name for p in owner.pets if task in p.tasks), "Unknown")
			status = "✓ Done" if task.completed else "⏳ Pending"
			time_str = task.scheduled_at.strftime("%I:%M %p") if task.scheduled_at else "No time set"
			
			print(f"\n{i}. [{status}] {task.title}")
			print(f"   Time: {time_str}")
			print(f"   Pet: {pet_name}")
			print(f"   Description: {task.description}")
	else:
		print("\nNo tasks scheduled for today.")

	# Show pending tasks summary
	print("\n" + "=" * 60)
	print("PENDING TASKS SUMMARY")
	print("=" * 60)
	pending = scheduler.get_pending_tasks()
	print(f"Total pending tasks: {len(pending)}")
	for task in pending:
		pet_name = next((p.name for p in owner.pets if task in p.tasks), "Unknown")
		print(f"  • {task.title} ({pet_name})")

	# Show food inventory
	print("\n" + "=" * 60)
	print("FOOD INVENTORY")
	print("=" * 60)
	for pet in owner.pets:
		print(f"\n{pet.name}:")
		for food in pet.foods:
			status = "🔴 Low Stock!" if food.needs_refill() else "✓ OK"
			print(f"  • {food.brand} ({food.type}): {food.quantity} units {status}")

	# Mark a task as complete and show the timestamp
	print("\n" + "=" * 60)
	print("COMPLETING A TASK")
	print("=" * 60)
	task1.complete()
	print(f"\nMarked '{task1.title}' as complete.")
	print(f"Completed at: {task1.completed_at}")

	# Show updated pending tasks
	print("\n" + "=" * 60)
	print("UPDATED PENDING TASKS")
	print("=" * 60)
	pending_updated = scheduler.get_pending_tasks()
	print(f"Total pending tasks: {len(pending_updated)}")
	for task in pending_updated:
		pet_name = next((p.name for p in owner.pets if task in p.tasks), "Unknown")
		print(f"  • {task.title} ({pet_name})")


if __name__ == "__main__":
	main()
