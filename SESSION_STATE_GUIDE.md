# Session State Pattern: Persistent Data in Streamlit

## Problem
Streamlit reruns your entire script from top to bottom every time a user interacts with a widget (clicks a button, types in a text box, etc.). This means any objects created at the module level would be recreated and lose their state.

## Solution: st.session_state
`st.session_state` is a **persistent dictionary** that survives reruns. Think of it as a "vault" where you store data between user interactions.

## Pattern Used in app.py

### 1. Initialize on First Load
```python
if "owner" not in st.session_state:
    st.session_state.owner = None
```
- Check if a key exists in session_state
- If not, initialize it with a default value
- This only runs once per session (or until the browser is closed)

### 2. Create or Retrieve
```python
if st.button("Create/Update Owner"):
    if st.session_state.owner is None:
        # Create new Owner (first time)
        st.session_state.owner = Owner(name=owner_name)
    else:
        # Update existing Owner (already created)
        st.session_state.owner.name = owner_name
```
- Check if object exists before creating
- Store it in session_state for persistence
- On next rerun, the object is still there!

### 3. Access Persistent Data
```python
if st.session_state.owner:
    st.write(f"Owner: {st.session_state.owner.name}")
    st.write(f"Pets: {len(st.session_state.owner.pets)}")
```
- Any code that reads from session_state gets the persistent value
- Add pets, tasks, etc. and they persist across reruns

## Key Concepts

| Concept | Behavior |
|---------|----------|
| **First visit** | `"owner" not in st.session_state` is True → initialize to None |
| **Create Owner** | `st.session_state.owner = Owner(...)` → stored in vault |
| **Rerun (button click)** | Script reruns but `st.session_state.owner` is NOT None → data persists |
| **Add pet/task** | `st.session_state.owner.add_pet(...)` → modifies persisted object |
| **Close browser** | Session ends → st.session_state is cleared |

## What Persists in Your App

✅ **Owner** object (name, list of pets)  
✅ **Pets** added to Owner (names, species, tasks)  
✅ **Tasks** added to pets (titles, descriptions, completed status)  
✅ **Session tasks** list (pending tasks in memory)

## Next Steps

- Add a "Generate Schedule" button that calls `Scheduler(owner=st.session_state.owner)`
- Display results using Streamlit components
- Add persistence for completed tasks across reruns
