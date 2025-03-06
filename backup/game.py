# game.py
import streamlit as st
import sqlite3
import datetime
from datetime import datetime
# Assuming you have a DatabaseService class
from database import DatabaseService
# Assuming you have an evaluate_code function
from llm_service import evaluate_code

from app import get_sign_in_url, generate_sidebar_links


def main():
    st.set_page_config(page_title="Speed Coding Game",
                       page_icon="🎯", layout="centered")

    with st.sidebar:
        if st.session_state.get("user"):
            generate_sidebar_links()
            st.markdown('---')
        else:
            st.write("Please log in to access the application.")
            st.markdown(
                f"[Click here to log in with Azure AD]({get_sign_in_url()})")

    st.title("Speed Coding Game 🎯")

    # Game Mode Selection
    game_mode = st.radio("Select Game Mode",
                         ("Submit Code", "Fill in the Blanks"))

    if game_mode == "Submit Code":
        submit_code_mode()
    elif game_mode == "Fill in the Blanks":
        fill_in_blanks_mode()


def submit_code_mode():
    st.subheader("Submit Code Mode")

    problem = "Write a Python function to calculate the factorial of a number."
    st.markdown(f"**Problem Statement:** {problem}")

    # User Code Input
    user_code = st.text_area(
        "Your Code:",
        "def factorial(n):\n    if n == 0:\n        return 1\n    else:\n        return n * factorial(n-1)",
        height=200
    )

    # Submit Button
    if st.button("Submit Code"):
        with st.spinner("Evaluating your code..."):
            correct_answer = """def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)"""

            # Evaluate the user's code
            overall_score, feedback = evaluate_code(
                problem, user_code, correct_answer)

            # Display Results
            st.success(f"**Overall Score:** {overall_score:.2f} / 10.0")
            st.info(f"**Feedback:** {feedback}")

            # Show Correct Answer Button
            if st.button("Show Correct Answer"):
                st.code(correct_answer, language='python')


def fill_in_blanks_mode():
    st.subheader("🎯 Fill in the Blanks Mode")

    problem = "Write a Python function to calculate the factorial of a number."
    st.markdown(f"**Problem Statement:** {problem}")

    # Function with Blanks
    code_with_blanks = [
        "def factorial(n):",
        "    if n == __:",
        "        return 1",
        "    else:",
        "        return n * factorial(n-1)"
    ]

    # Initialize placeholders
    inputs = {}

    st.markdown(
        "**Your Task:** Fill in the blanks (`__`) in the following function.")

    # Display the code with input fields replacing the blanks
    for idx, line in enumerate(code_with_blanks):
        if '__' in line:
            # Split the line at the blank
            parts = line.split('__')
            # Create a placeholder for this line
            empty_placeholder = st.empty()
            with empty_placeholder.container():
                # Create three columns: pre-blank, input, post-blank
                col1, col2, col3 = st.columns([2, 3, 2])
                with col1:
                    # Display pre-blank part in monospace font
                    st.markdown(f"`{parts[0]}`")
                with col2:
                    # Input field for the blank
                    user_input = st.text_input(
                        "",
                        value="",
                        key=f"input_{idx}",
                        placeholder="Fill here",
                        help="Enter the missing value."
                    )
                    inputs[idx] = user_input
                with col3:
                    # Display post-blank part in monospace font
                    st.markdown(f"`{parts[1]}`")
        else:
            # Display non-blank lines in monospace font
            st.markdown(f"`{line}`")

    # Submit Button
    if st.button("➡️ Submit Code"):
        with st.spinner("🔍 Evaluating your code..."):
            # Reconstruct the user's code by replacing blanks with inputs
            user_code = ""
            for idx, line in enumerate(code_with_blanks):
                if '__' in line:
                    filled_line = line.replace('__', inputs.get(idx, ''))
                    user_code += filled_line + "\n"
                else:
                    user_code += line + "\n"

            correct_answer = """def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)"""

            # Evaluate the user's code
            overall_score, feedback = evaluate_code(
                problem, user_code, correct_answer)

            # Display Results
            st.success(f"**Overall Score:** {overall_score:.2f} / 10.0")
            st.info(f"**Feedback:** {feedback}")

            # Show Correct Answer Button
            if st.button("📜 Show Correct Answer"):
                st.code(correct_answer, language='python')

    # Optional: Add a Reset Button to Clear Inputs
    if st.button("Reset"):
        for idx in inputs.keys():
            st.session_state[f"input_{idx}"] = ''


if __name__ == "__main__":
    main()
