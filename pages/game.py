# game.py

import streamlit as st
from datetime import datetime, timedelta
import random
from textwrap import dedent
from llm_service import LLMService
from app import get_sign_in_url, generate_sidebar_links

# Define the coding challenges
CHALLENGES = [
    {
        "question": "Write a Python function to add two numbers a and b.",
        "answer": dedent('''
        def add(a, b):
            return a + b
        ''').strip()
    },
    {
        "question": "Write a Python function to find the factorial of a number n.",
        "answer": dedent('''
        def factorial(n):
            if n == 0:
                return 1
            else:
                return n * factorial(n-1)
        ''').strip()
    },
    {
        "question": "Write a Python function to check if a number is even.",
        "answer": dedent('''
        def is_even(n):
            return n % 2 == 0
        ''').strip()
    },
    # Add more challenges as needed
]


def initialize_session_state():
    """Initialize session state variables."""
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'current_challenge' not in st.session_state:
        start_new_challenge()
    if 'end_time' not in st.session_state:
        st.session_state.end_time = datetime.now() + timedelta(seconds=60)
    if 'user_code' not in st.session_state:
        st.session_state.user_code = ""
    if 'feedback' not in st.session_state:
        st.session_state.feedback = ""
    if 'llm_service' not in st.session_state:
        st.session_state.llm_service = LLMService()


def start_new_challenge():
    """Select a new challenge and reset relevant session variables."""
    st.session_state.current_challenge = random.choice(CHALLENGES)
    st.session_state.end_time = datetime.now() + timedelta(seconds=60)
    st.session_state.user_code = ""
    st.session_state.feedback = ""


def display_sidebar():
    """Render the sidebar with navigation and user information."""
    with st.sidebar:
        if st.session_state.get("user"):
            generate_sidebar_links()
            st.markdown('---')
            st.write(f"**Score:** {st.session_state.score}")
        else:
            st.write("Please log in to access the application.")
            st.markdown(
                f"[Click here to log in with Azure AD]({get_sign_in_url()})")


def countdown_timer():
    """Display a countdown timer."""
    remaining_time = int((st.session_state.end_time -
                         datetime.now()).total_seconds())
    remaining_time = max(0, remaining_time)
    return remaining_time


def display_challenge():
    """Display the current coding challenge."""
    st.header("Coding Challenge 🎯")
    st.write(st.session_state.current_challenge["question"])


def get_user_code():
    """Render the code input area."""
    st.session_state.user_code = st.text_area(
        "Write your code here:",
        height=200,
        value=st.session_state.user_code,
        placeholder="Enter your Python code..."
    )


def submit_code():
    """Handle the code submission logic."""
    llm_service = st.session_state.llm_service
    correct_answer = st.session_state.current_challenge["answer"]
    user_code = st.session_state.user_code

    if not user_code.strip():
        st.error("Please write your code before submitting.")
        return

    with st.spinner("Evaluating your code..."):
        is_correct, feedback = llm_service.evaluate_code(
            user_code, correct_answer)

    if is_correct:
        st.success("✅ Correct! You earned 10 points.")
        st.session_state.score += 10
        st.success("Great job! Moving to the next challenge.")
        start_new_challenge()
    else:
        st.error("❌ Incorrect answer. Here's some feedback:")
        st.info(feedback)
        st.session_state.feedback = feedback


def display_feedback():
    """Display feedback if available."""
    if st.session_state.feedback:
        st.info("**Feedback:**")
        st.write(st.session_state.feedback)


def main():
    st.set_page_config(page_title="Speed Coding Game",
                       page_icon="🎯", layout="centered")
    st.title("Speed Coding Game 🎯")

    initialize_session_state()
    display_sidebar()
    display_challenge()
    get_user_code()

    remaining_time = countdown_timer()

    # Timer display
    timer_placeholder = st.empty()
    if remaining_time > 0:
        timer_placeholder.markdown(
            f"**Time remaining:** {remaining_time} seconds")
    else:
        timer_placeholder.warning("⏰ **Time's up!**")
        if st.button("New Challenge"):
            start_new_challenge()
            st.rerun()

    # Initialize LLMService (if not already done)
    if 'llm_service' not in st.session_state:
        st.session_state.llm_service = LLMService()

    # Submit button
    if remaining_time > 0:
        submit_disabled = False
    else:
        submit_disabled = True

    if st.button("Submit Code", disabled=submit_disabled):
        submit_code()

    # Display current score
    st.sidebar.markdown(f"**Your Score:** {st.session_state.score}")

    # Display feedback
    display_feedback()


if __name__ == "__main__":
    main()
