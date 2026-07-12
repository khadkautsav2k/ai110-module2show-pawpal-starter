import streamlit as st
from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, PetFood, Scheduler, TimelyCare

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")

# Initialize session state for Owner on first load
# Think of st.session_state as a persistent "vault" that survives page refreshes
if "owner" not in st.session_state:
	st.session_state.owner = None

if "selected_pet" not in st.session_state:
	st.session_state.selected_pet = None

# Owner Creation Section
st.markdown("### Step 1: Create or Load Owner")
owner_name = st.text_input("Owner name", value="Jordan", key="owner_input")

if st.button("Create/Update Owner"):
	# Check if Owner already exists in session_state
	if st.session_state.owner is None:
		# Create new Owner and store in session_state (persists across reruns)
		st.session_state.owner = Owner(name=owner_name)
		st.success(f"✅ Owner '{owner_name}' created and saved to memory!")
	else:
		# Update existing Owner's name
		st.session_state.owner.name = owner_name
		st.info(f"📝 Owner name updated to '{owner_name}'")

# Display current Owner status
if st.session_state.owner:
	st.write(f"**Current Owner:** {st.session_state.owner.name}")
	st.write(f"**Pets managed:** {len(st.session_state.owner.pets)}")
else:
	st.warning("⚠️ No owner created yet. Create one above to get started!")

st.divider()

# Pet Management Section (only available after Owner is created)
if st.session_state.owner:
	st.markdown("### Step 2: Add Pet")
	col1, col2 = st.columns(2)
	with col1:
		pet_name = st.text_input("Pet name", value="Mochi", key="pet_input")
	with col2:
		species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])

	if st.button("Add Pet"):
		# Create new Pet and add to Owner (stored in session_state)
		new_pet = Pet(name=pet_name, species=species)
		st.session_state.owner.add_pet(new_pet)
		st.success(f"✅ Added {pet_name} ({species}) to {st.session_state.owner.name}'s pets!")
		st.rerun()

	# Display current pets with selection
	if st.session_state.owner.pets:
		st.write(f"**Pets for {st.session_state.owner.name}:**")
		pet_names = [f"{i+1}. {p.name} ({p.species})" for i, p in enumerate(st.session_state.owner.pets)]
		selected_pet_display = st.selectbox("Select a pet to add tasks:", pet_names, key="pet_selector")
		
		# Extract selected pet index
		selected_idx = int(selected_pet_display.split(".")[0]) - 1
		st.session_state.selected_pet = st.session_state.owner.pets[selected_idx]
		
		# Show selected pet summary
		if st.session_state.selected_pet:
			with st.expander(f"📋 {st.session_state.selected_pet.name}'s Details"):
				st.write(f"**Name:** {st.session_state.selected_pet.name}")
				st.write(f"**Species:** {st.session_state.selected_pet.species}")
				st.write(f"**Tasks:** {len(st.session_state.selected_pet.tasks)}")
				if st.session_state.selected_pet.tasks:
					st.write("**Task List:**")
					for task in st.session_state.selected_pet.tasks:
						status = "✅" if task.completed else "⏳"
						st.write(f"  {status} {task.title}")
	else:
		st.info("No pets yet. Add one above!")

st.divider()

st.markdown("### Step 3: Add Tasks to Selected Pet")
st.caption("Tasks are stored in the selected pet and persist across page refreshes.")

if st.session_state.owner and st.session_state.selected_pet:
	col1, col2, col3 = st.columns(3)
	with col1:
		task_title = st.text_input("Task title", value="Morning walk", key="task_title_input")
	with col2:
		duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20, key="task_duration_input")
	with col3:
		priority = st.selectbox("Priority", ["low", "medium", "high"], index=2, key="task_priority_input")

	if st.button("Add Task to Pet"):
		# Create Task object with scheduled time (1 hour from now for demo)
		new_task = Task(
			title=task_title,
			description=f"Priority: {priority}",
			scheduled_at=datetime.now() + timedelta(hours=1)
		)
		# Add task to selected pet using the Pet.add_task() method
		st.session_state.selected_pet.add_task(new_task)
		st.success(f"✅ Added '{task_title}' to {st.session_state.selected_pet.name}!")
		st.rerun()

	# Display pet's tasks
	if st.session_state.selected_pet.tasks:
		st.write(f"**Tasks for {st.session_state.selected_pet.name}:**")
		for i, task in enumerate(st.session_state.selected_pet.tasks, 1):
			status = "✅ Done" if task.completed else "⏳ Pending"
			overdue = "🔴 OVERDUE" if task.is_overdue() else ""
			st.write(f"  {i}. [{status}] {task.title} {overdue}")
			
			# Option to mark task as complete
			if not task.completed:
				if st.button(f"Mark '{task.title}' complete", key=f"complete_{task.id}"):
					task.complete()
					st.success(f"✅ Marked '{task.title}' as complete!")
					st.rerun()
	else:
		st.info(f"No tasks yet for {st.session_state.selected_pet.name}. Add one above!")
else:
	st.warning("⚠️ Please create an owner and select a pet first.")

st.divider()

st.subheader("📅 Today's Schedule")
st.caption("Generate your pet's daily schedule using the Scheduler logic.")

if st.button("Generate Today's Schedule"):
	if st.session_state.owner and st.session_state.owner.pets:
		# Create Scheduler instance and call backend logic
		scheduler = Scheduler(owner=st.session_state.owner)
		
		# Get today's tasks using the Scheduler method
		todays_tasks = scheduler.get_todays_schedule()
		pending_tasks = scheduler.get_pending_tasks()
		overdue_tasks = scheduler.get_tasks_to_execute()
		
		# Display schedule results
		st.success("✅ Schedule generated!")
		
		with st.expander(f"📋 Today's Tasks ({len(todays_tasks)} total)", expanded=True):
			if todays_tasks:
				for task in todays_tasks:
					pet_owner = next((p for p in st.session_state.owner.pets if task in p.tasks), None)
					status = "✅" if task.completed else "⏳"
					time_str = task.scheduled_at.strftime("%I:%M %p") if task.scheduled_at else "No time"
					st.write(f"{status} **{task.title}** (by {pet_owner.name if pet_owner else 'Unknown'})")
					st.write(f"   ⏰ {time_str}")
			else:
				st.info("No tasks scheduled for today.")
		
		with st.expander(f"⏳ All Pending Tasks ({len(pending_tasks)} total)"):
			if pending_tasks:
				for task in pending_tasks:
					pet_owner = next((p for p in st.session_state.owner.pets if task in p.tasks), None)
					st.write(f"• {task.title} ({pet_owner.name if pet_owner else 'Unknown'})")
			else:
				st.info("All tasks completed!")
		
		with st.expander(f"🔴 Overdue Tasks ({len(overdue_tasks)} total)"):
			if overdue_tasks:
				for task in overdue_tasks:
					pet_owner = next((p for p in st.session_state.owner.pets if task in p.tasks), None)
					st.error(f"⚠️ {task.title} ({pet_owner.name if pet_owner else 'Unknown'})")
			else:
				st.success("No overdue tasks!")
else:
	st.warning("⚠️ Please create an owner and add pets with tasks first.")
