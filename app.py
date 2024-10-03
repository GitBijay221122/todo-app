import streamlit as st
import functions  # Assuming this imports your custom functions
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Add custom CSS for the background image
def set_background(image_path):
    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("{image_path}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        opacity: 0.9;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Set the background using the uploaded image
set_background("/mnt/data/background.webp")

# Initialize session state for login status
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'todos' not in st.session_state:
    st.session_state.todos = []

# Function to handle login and reset session state
def login(email):
    st.session_state.logged_in = True
    st.session_state.user_email = email
    st.session_state.todos = []  # Clear task list for new login
    st.session_state.show_add_task = False  # Reset task adding menu state

# Function to handle logout and reset session state
def logout():
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.todos = []
    st.session_state.show_add_task = False
    st.success("You have been logged out.")

# Function to send email notification
def send_email_notification(task, task_date, task_time, user_email):
    try:
        sender_email = "bijay221122@gmail.com"
        sender_password = "ueeivhfrmfxjqwic"  # Use app-specific password from Gmail

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = user_email
        msg['Subject'] = "Task Reminder"
        body = f"Reminder! You have a task: '{task}' scheduled for {task_date} at {task_time}."
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Start TLS for security
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        st.success(f"Reminder email sent to {user_email} for task: '{task}'")
    except Exception as e:
        st.error(f"Failed to send email notification: {e}")

# Function to check if any task is due in the next 10 minutes
def check_for_upcoming_tasks():
    current_time = datetime.now()
    tasks_to_notify = []

    for task in st.session_state.todos:
        task_detail = task.strip().split(' | ')
        if len(task_detail) == 3:
            task_name, task_date_str, task_time_str = task_detail
            task_date = datetime.strptime(task_date_str, '%Y-%m-%d').date()
            task_time = datetime.strptime(task_time_str, '%H:%M:%S').time()

            task_datetime = datetime.combine(task_date, task_time)
            time_until_task = task_datetime - current_time

            # If task is within the next 10 minutes and has not passed
            if timedelta(minutes=0) < time_until_task <= timedelta(minutes=10):
                tasks_to_notify.append((task_name, task_date_str, task_time_str))

    # Send reminders for upcoming tasks
    for task_name, task_date, task_time in tasks_to_notify:
        send_email_notification(task_name, task_date, task_time, st.session_state.user_email)

# Login section
if not st.session_state.logged_in:
    st.title("Login to Your To-Do List")
    email = st.text_input("Enter your email:", "")
    
    if st.button("Login"):
        if email:
            login(email)  # Call login and reset session state
            st.success(f"Welcome, {email}!")
        else:
            st.error("Please enter an email address.")
else:
    # Check for logout
    if st.button("Logout"):
        logout()

    # Load tasks specific to the logged-in user
    st.session_state.todos = functions.get_tdos()  # Assume functions.get_tdos() fetches user-specific tasks

    # Check if there are any tasks due in the next 10 minutes
    check_for_upcoming_tasks()

    # Application Title
    st.title("To-Do List with Date and Time")

    # Expander for Task Adding Section
    with st.expander("Add a New Task"):
        st.header("Add a New Task")
        
        # Use columns for task, date, and time inputs
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_task = st.text_input("Task")
        
        with col2:
            new_date = st.date_input("Select a date", min_value=datetime.today())
        
        with col3:
            new_time = st.time_input("Select a time")
        
        if st.button("Add Task"):
            if new_task:
                # Format task with date and time
                task_with_time = f"{new_task} | {new_date} | {new_time}"

                # Append the new task to todos
                st.session_state.todos.append(task_with_time + '\n')

                # Write the updated list back to the file
                functions.write_tdos(st.session_state.todos)

                # Display success message
                st.success(f"Task '{new_task}' added successfully with date {new_date} and time {new_time}!")

                # Send email notification (trigger immediately after task creation)
                task_datetime = datetime.combine(new_date, new_time)
                time_until_task = task_datetime - datetime.now()

                # Send a notification for tasks within 10 minutes
                if time_until_task <= timedelta(minutes=10):
                    send_email_notification(new_task, new_date, new_time, st.session_state.user_email)

            else:
                st.error("Please enter a task description.")

    # Initialize lists for completed and remaining tasks
    remaining_tasks = []
    completed_tasks = []

    # Expander for Task Display Section
    with st.expander("Your Tasks"):
        # Display existing tasks
        if st.session_state.todos:  # Only show tasks if there are any
            for index, task in enumerate(st.session_state.todos):
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

    # Expander for Remaining Tasks Section
    with st.expander("Remaining Tasks"):
        st.header("Remaining Tasks")
        if remaining_tasks:
            for task in remaining_tasks:
                st.write(task.strip())  # Display remaining tasks without extra newlines
        else:
            st.write("No remaining tasks.")

    # Expander for Completed Tasks Section
    with st.expander("Completed Tasks"):
        st.header("Completed Tasks")
        if completed_tasks:
            for task in completed_tasks:
                st.write(task.strip())  # Display completed tasks without extra newlines
        else:
            st.write("No completed tasks.")

    # Optional: Display a message if no tasks are available to display
    if not st.session_state.todos:
        st.write("No tasks available. Please add tasks to display.")
