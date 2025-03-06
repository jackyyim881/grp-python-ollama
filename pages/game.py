
import streamlit as st
from llm_service import evaluate_code, evaluate_with_chatxai
import json
from app import get_sign_in_url, generate_sidebar_links
import sys
import io
from code_editor import code_editor


def is_authenticated():
    """
    Check if the user is authenticated.
    """
    return 'user' in st.session_state and st.session_state.user is not None


def load_questions_from_json():
    """Load questions from a JSON file."""
    with open('./data/game_questions.json', 'r') as file:
        data = json.load(file)
    return data['questions']


def main():
    st.set_page_config(page_title="Speed Coding Game",
                       page_icon="🎯", layout="centered")
    if not is_authenticated():
        st.title("Access Denied ⚠️")
        st.warning("Please log in to use the assistant.")
        st.stop()
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
    game_mode = st.radio("Select Game Mode", ("Submit Code",
                         "Fill in the Blanks", "Theory Questions"))

    if game_mode == "Submit Code":
        submit_code_mode()
    elif game_mode == "Fill in the Blanks":
        fill_in_blanks_mode()
    elif game_mode == "Theory Questions":
        theory_questions_mode()


def submit_code_mode():
    st.subheader("Submit Code Mode")

    # Load questions from the JSON
    questions = load_questions_from_json()

    # Display questions one by one
    for question in questions:
        if question['type'] != 'submit_code':
            continue  # Skip non-submit code questions

        st.markdown(f"**Problem Statement:** {question['question']}")

        # Display the code template if available
        code_template = question.get('code_template', "")

        user_code = code_editor(
            code_template, lang='python', height=400, key=f"code_{question['id']}", theme="material")

        # Submit Button
        if st.button(f"Submit Code for Question {question['id']}"):
            with st.spinner("Evaluating your code..."):
                correct_answer = question.get('correct_answer', '')

                # Run the code and capture the output
                output = run_python_code(user_code)

                st.success(f"**Output:**")
                st.code(output, language='python')

                # Evaluate the code using some evaluation logic (assumed to be in `evaluate_code`)
                overall_score, feedback = evaluate_code(
                    question['question'], user_code, correct_answer)

                st.success(f"**Overall Score:** {overall_score:.2f} / 10.0")
                st.info(f"**Feedback:** {feedback}")

                if st.button(f"Show Correct Answer for Question {question['id']}"):
                    st.code(correct_answer, language='python')


def run_python_code(code):
    """Execute the submitted Python code safely and return the output or error message."""
    old_stdout = sys.stdout  # Backup the original stdout
    # Redirect stdout to capture print statements
    sys.stdout = mystdout = io.StringIO()

    try:
        exec(code)  # Execute the user's code
        output = mystdout.getvalue()  # Get the captured output
    except Exception as e:
        output = f"Error: {str(e)}"  # Capture any errors that occur
    finally:
        sys.stdout = old_stdout  # Reset stdout back to the original

    return output


def fill_in_blanks_mode():
    st.subheader("🎯 Fill in the Blanks Mode")

    # Load questions from the JSON (Assuming you have the `questions` list loaded)
    questions = load_questions_from_json()

    # Display fill-in-the-blank questions
    for question in questions:
        if question['type'] != 'fill_in_the_blank':
            continue  # Skip other types of questions

        st.markdown(f"**Problem Statement:** {question['question']}")

        # Get the code with blanks from the question data
        code_with_blanks = question.get('code_with_blanks', [])

        # Initialize placeholders for user inputs if not already initialized
        if 'inputs' not in st.session_state:
            st.session_state['inputs'] = {}

        st.markdown(
            "**Your Task:** Fill in the blanks (`__`) in the following function.")

        # Combine the code with blanks into one block of text
        full_code = "\n".join(code_with_blanks)

        # Replace blanks (`__`) with input fields dynamically
        blank_count = full_code.count('__')  # Count how many blanks exist
        for idx in range(blank_count):
            # Create a unique key for each input box to store the value in session state
            user_input = st.text_input(
                f"Fill in blank {idx + 1}",
                value=st.session_state['inputs'].get(f"input_{idx}", ""),
                key=f"input_{idx}",
                placeholder="Enter here",
                help="Enter the missing value."
            )
            st.session_state['inputs'][f"input_{idx}"] = user_input

        # Display the code with blanks as input fields
        filled_code = full_code
        for idx in range(blank_count):
            # Replace `__` with the user input value from session state
            filled_code = filled_code.replace(
                '__', st.session_state['inputs'].get(f"input_{idx}", ''), 1)

        # Display the code with the blanks filled in (updated code after user input)
        st.text_area("Code with your answers", value=filled_code,
                     height=200, disabled=False, key=f"filled_code_{question['id']}")

        # Submit Button
        if st.button(f"➡️ Submit Code for {question['id']}"):
            with st.spinner("🔍 Evaluating your code..."):
                # Evaluate the user's code (Assuming evaluate_code is available)
                user_code = filled_code
                correct_answer = question.get('correct_answer', '')

                # Evaluate the user's code
                overall_score, feedback = evaluate_with_chatxai(
                    question['question'], user_code, correct_answer
                )

                # Display Results
                st.success(f"**Overall Score:** {overall_score:.2f} / 10.0")
                st.info(f"**Feedback:** {feedback}")

                if st.button(f"📜 Show Correct Answer for {question['id']}"):
                    st.code(correct_answer, language='python')

        # Optional: Add a Reset Button to Clear Inputs
        if st.button(f"Reset Inputs for {question['id']}", key=f"reset_{question['id']}"):
            st.session_state['inputs'] = {}
            st.rerun()


def theory_questions_mode():
    st.subheader("Theory Questions Mode")

    # Load questions from the JSON
    questions = load_questions_from_json()

    # Store the answers to the questions
    answers = {}

    # Display theory questions
    for question in questions:
        if question['type'] == 'multiple_choice':
            st.markdown(
                f"**Question {question['id']}:** {question['question']}")
            options = question['options']
            selected_option = st.radio(
                "Select your answer:", options, key=f"q{question['id']}")
            answers[question['id']] = selected_option  # Store selected answer

            # Submit button
            submit_button = st.button(f"Submit Answer for Question {
                                      question['id']}", key=f"submit_q{question['id']}")

            if submit_button:
                if selected_option:
                    if selected_option == question['correct_answer']:
                        st.success(f"**Question {question['id']}**: Correct!")
                    else:
                        st.error(f"**Question {question['id']}**: Incorrect. The correct answer is: {
                                 question['correct_answer']}")
                else:
                    st.warning(
                        f"**Question {question['id']}**: Please select an answer!")

            # Show explanation button
            if st.button(f"Show Explanation for Question {question['id']}", key=f"explanation_q{question['id']}"):
                st.info(question['explanation'])

        elif question['type'] == 'true_false':
            st.markdown(
                f"**Question {question['id']}:** {question['question']}")
            selected_option = st.radio(
                "True or False", ["True", "False"], key=f"q{question['id']}")
            answers[question['id']] = selected_option  # Store selected answer

            # Submit button
            submit_button = st.button(f"Submit Answer for Question {
                                      question['id']}", key=f"submit_q{question['id']}")

            if submit_button:
                if selected_option:
                    correct = question['correct_answer']
                    if (selected_option == "True" and correct == "True") or (selected_option == "False" and correct == "False"):
                        st.success(f"**Question {question['id']}**: Correct!")
                    else:
                        st.error(
                            f"**Question {question['id']}**: Incorrect. The correct answer is: {correct}")
                else:
                    st.warning(
                        f"**Question {question['id']}**: Please select an answer!")

            # Show explanation button
            if st.button(f"Show Explanation for Question {question['id']}", key=f"explanation_q{question['id']}"):
                st.info(question['explanation'])


if __name__ == "__main__":
    main()
