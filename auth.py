# auth.py
import streamlit as st
from config import Config
from datetime import datetime


class AuthProvider:
    def __init__(self, users, db_service):
        """
        Initialize the AuthProvider with a dictionary of users.
        :param users: Dictionary mapping usernames to passwords.
        """
        self.users = users
        self.db_service = db_service
        self.initialize_session_state()

    def initialize_session_state(self):
        """
        Initialize session state variables if they don't exist.
        - user_state: Tracks the current user's username, password, and login status.
        - failed_attempts: Counts consecutive failed login attempts.
        """
        if 'user_state' not in st.session_state:
            st.session_state.user_state = {
                "username": '',      # Current user's username
                "password": '',      # Current user's password
                "logged_in": False   # Login status
            }

        if 'failed_attempts' not in st.session_state:
            st.session_state.failed_attempts = 0

    def login(self):
        """
        Render the login form and handle authentication.
        Displays login fields if the user is not logged in.
        """
        # Only display the login form if the user is not logged in
        if not st.session_state.user_state['logged_in']:
            st.sidebar.title("User Login")
            username = st.sidebar.text_input("Student ID")
            password = st.sidebar.text_input("Password", type="password")
            submit = st.sidebar.button("Login")

            if submit:
                if st.session_state.failed_attempts >= 5:
                    st.sidebar.error(
                        "Too many failed attempts. Please try again later.")
                    return

                if username in self.users and password == self.users[username]:
                    # Successful login
                    st.session_state.user_state['username'] = username
                    st.session_state.user_state['password'] = password
                    st.session_state.user_state['logged_in'] = True
                    st.session_state.failed_attempts = 0  # Reset failed attempts
                    st.sidebar.success(f"Welcome {username}!")

                    # Record login time in database
                    login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.db_service.insert_login_time(username, login_time)

                else:
                    # Failed login attempt
                    st.session_state.failed_attempts += 1
                    st.sidebar.error("Invalid Student ID or Password")

    def logout(self):
        """
        Render the logout button and handle logout action.
        Displays logout button if the user is logged in.
        """
        # Only display the logout button if the user is logged in
        if st.session_state.user_state['logged_in']:
            st.sidebar.title("User Logout")
            if st.sidebar.button("Logout"):
                # Reset user state
                st.session_state.user_state = {
                    "username": '',
                    "password": '',
                    "logged_in": False
                }
                # Reset other session state variables if necessary
                st.session_state.view_results = False
                st.session_state.submitted_questions = set()
                st.session_state.failed_attempts = 0
                st.sidebar.success("You have been logged out successfully!")
                # Rerun the script to update the UI


class AuthService:
    def __init__(self, auth_provider):
        """
        Initialize AuthService with an instance of AuthProvider.
        :param auth_provider: Instance of AuthProvider.
        """
        self.auth_provider = auth_provider

    def render_auth(self):
        """
        Conditionally render login or logout based on authentication state.
        """
        if not st.session_state.user_state['logged_in']:
            self.auth_provider.login()
        else:
            self.auth_provider.logout()
