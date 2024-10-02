import streamlit as st
import functions  # Importing the 'functions' module
from datetime import datetime

# Initialize session state for login status
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""

# Function to handle login
def login(email):
    st.session_state.logged_in = True
    st.session_state.user_email = email

# Login section
if not st.session_state.logged_in:
    st.title("Login to Your To-Do List")
    email = st.text_input("Enter your email:", "")
    if st.button("Login"):
        if email:
            login(email)
            st.success(f"Welcome, {email}!")
        else:
            st.error("Please enter an email address.")
else:
    # Load existing tasks for the logged-in user
    todos = functions.get_tdos()  # Load tasks from the file

    # Application Title
    st.title("To-Do List with Date and Time")

    # State management for showing the task adding menu
    if 'show_add_task' not in st.session_state:
        st.session_state.show_add_task = False

    # Toggle button for showing/hiding the task adding menu
    if st.button("Toggle Task Adding Menu"):
        st.session_state.show_add_task = not st.session_state.show_add_task

    # Display task adding section if toggled
    if st.session_state.show_add_task:
        st.header("Add a New Task")
        new_task = st.text_input("Task")
        new_date = st.date_input("Select a date for the task", min_value=datetime.today())
        new_time = st.time_input("Select a time for the task")

        if st.button("Add Task"):
            if new_task:
                # Format task with date and time
                task_with_time = f"{new_task} | {new_date} | {new_time}"

                # Append the new task to todos
                todos.append(task_with_time + '\n')

                # Write the updated list back to the file
                functions.write_tdos(todos)

                # Display success message
                st.success(f"Task '{new_task}' added successfully with date {new_date} and time {new_time}!")
            else:
                st.error("Please enter a task description.")

    # Initialize lists for completed and remaining tasks
    remaining_tasks = []
    completed_tasks = []

    # Display existing tasks
    if todos:  # Only show display button if there are tasks
        for index, task in enumerate(todos):
            task_detail = task.strip().split(' | ')  # Assuming ' | ' separates task, date, and time
            if len(task_detail) == 3:
                task_name, task_date, task_time = task_detail
                # Create a checkbox for each task
                if st.checkbox(f"**Task:** {task_name} | **Date:** {task_date} | **Time:** {task_time}", key=index):
                    completed_tasks.append(task)  # Mark the task as completed
                else:
                    remaining_tasks.append(task)  # Keep it as remaining

        # Save completed tasks back to the file if checked
        if st.button("Update Tasks"):
            if completed_tasks:
                # Save remaining tasks back to the file
                functions.write_tdos(remaining_tasks)
                st.success("Completed tasks removed successfully!")

    # Display remaining tasks
    st.header("Remaining Tasks")
    if remaining_tasks:
        for task in remaining_tasks:
            st.write(task.strip())  # Display remaining tasks without extra newlines
    else:
        st.write("No remaining tasks.")

    # Display completed tasks
    st.header("Completed Tasks")
    if completed_tasks:
        for task in completed_tasks:
            st.write(task.strip())  # Display completed tasks without extra newlines
    else:
        st.write("No completed tasks.")

    # Optional: Display a message if no tasks are available to display
    if not todos:
        st.write("No tasks available. Please add tasks to display.")
