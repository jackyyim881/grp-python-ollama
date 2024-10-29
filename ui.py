# ui.py
import streamlit as st
from streamlit_elements import elements, mui
from config import Config
import random


class UIService:
    def __init__(self, db_service, question_loader, llm_service):
        self.db_service = db_service
        self.question_loader = question_loader
        self.llm_service = llm_service

        # Encouragement messages
        self.encouragement_messages_correct = [
            "Excellent work!",
            "Fantastic job!",
            "You're on fire!",
            "Keep up the great effort!",
            "You're mastering this topic!"
        ]

        self.encouragement_messages_incorrect = [
            "Don't worry, you'll get it next time!",
            "Keep trying, practice makes perfect!",
            "Stay positive, you'll improve!",
            "Review the material and try again!",
            "Don't give up!"
        ]

    def render(self):
        """
        Render the main UI of the application.
        """
        # User information is already handled in app.py
        username = st.session_state.user.get('name', 'User')

        # Fetch login times and progress
        email = st.session_state.user.get('preferred_username', 'unknown')
        login_count = self.db_service.get_login_count(email)
        total_questions_answered = self.db_service.get_total_questions_answered(
            email)
        total_correct_answers = self.db_service.get_total_correct_answers(
            email)

        # Provide encouragement based on login count
        if login_count == 0:
            st.sidebar.write(
                "Welcome to your first session! Let's get started!")
        elif login_count <= 5:
            st.sidebar.write(f"Welcome back! This is your {
                             login_count}th session. Keep up the good work!")
        else:
            st.sidebar.write(f"You're on a roll! This is your {
                             login_count}th session. Keep pushing forward!")

        # Provide encouragement based on progress
        if total_questions_answered == 0:
            st.sidebar.write(
                "You haven't answered any questions yet. Let's dive in!")
        else:
            st.sidebar.write(f"You've answered {total_questions_answered} questions with {
                             total_correct_answers} correct answers. Keep it up!")

        # Display sidebar menu and main content
        self.sidebar_menu()

        if st.session_state.get('view_results', False):
            self.show_results()
            self.hello_world()
        else:
            self.show_questions()

    def sidebar_menu(self):
        st.sidebar.success("You are logged in!")
        st.sidebar.write("Keep up the good work! You are doing great!")
        if 'view_results' not in st.session_state:
            st.session_state.view_results = False

        if st.sidebar.button("Hello World"):
            st.session_state.view_results = False

        if st.sidebar.button("View Assessment Results"):
            st.session_state.view_results = True
        elif st.sidebar.button("Answer Questions"):
            st.session_state.view_results = False

    def show_results(self):
        st.subheader("Assessment Results")
        email = st.session_state.user.get('preferred_username', 'unknown')
        results = self.db_service.fetch_results(email)
        if results:
            correct_count = sum(result[4] for result in results)
            total = len(results)
            st.write(f"You answered {correct_count} out of {
                     total} questions correctly.")
            for result in results:
                st.write(f"**Topic:** {result[0]}")
                st.write(f"**Question:** {result[1]}")
                st.write(f"**Your Answer:** {result[2]}")
                st.write(f"**Correct Answer:** {result[3]}")
                st.write(f"**Correct:** {'Yes' if result[4] else 'No'}")
                st.write(f"**Explanation:** {result[5]}")
                st.write("---")
            if st.sidebar.button("Show Correct Answers Summary with Graph"):
                self.show_summary_graph(results)
        else:
            st.write("No assessment results found.")

    def hello_world(self):
        with elements("new_element"):
            mui.Typography(variant="h1", children="Hello World!")

    def show_summary_graph(self, results):
        correct_answers_count = sum(result[4] for result in results)
        total_answers_count = len(results)

        with elements('correct_answers_summary'):
            mui.Box(
                sx={"padding": "16px", "maxWidth": "400px", "margin": "auto"},
                children=[
                    mui.Typography(variant="h5", gutterBottom=True,
                                   children="Summary of Correct vs Incorrect Answers"),
                    mui.Typography(variant="subtitle1", gutterBottom=True,
                                   children=f"Total Questions: {total_answers_count}"),
                    mui.Typography(variant="subtitle1", gutterBottom=True,
                                   children=f"Correct Answers: {correct_answers_count}"),
                    mui.LinearProgress(variant="determinate", value=(
                        correct_answers_count / total_answers_count) * 100, color="primary")
                ]
            )

    def show_questions(self):
        st.subheader("Select a Python Topic for Self-Assessment")
        topic = st.selectbox("Choose a topic:", [
                             "Set", "Tuple", "Anonymous Function"])

        if topic:
            st.write(f"You have selected: {topic}")
            st.write("Let's get started with the assessment!")

            if 'submitted_questions' not in st.session_state:
                st.session_state.submitted_questions = set()

            topic_questions = self.question_loader.load_questions().get(
                topic, [])
            for i, q in enumerate(topic_questions):
                if i not in st.session_state.submitted_questions:
                    st.write(f"**Question {i + 1}:** {q['question']}")
                    answer = st.radio("Select an answer:",
                                      q['options'], key=f"q_{i}")
                    if st.button(f"Submit Answer for Question {i + 1}", key=f"submit_{i}"):
                        correct = 1 if answer == q['answer'] else 0
                        if correct:
                            st.success("Correct! Great job!")
                        else:
                            st.error("Oops! That's not correct. Keep trying!")
                        st.session_state.submitted_questions.add(i)

                        # Store the result
                        email = st.session_state.user.get(
                            'preferred_username', 'unknown')
                        self.db_service.insert_result(
                            username=email,
                            topic=topic,
                            question=q['question'],
                            user_answer=answer,
                            correct_answer=q['answer'],
                            correct=correct,
                            explanation=''
                        )

                        # Fetch updated performance data
                        performance_data = self.db_service.get_student_performance(
                            email)

                        # Get encouragement from LLM
                        encouragement = self.llm_service.get_encouragement(
                            performance_data)

                        # Display the LLM-generated encouragement
                        st.write(encouragement)

            # Final encouragement and explanations
            if len(st.session_state.submitted_questions) == len(topic_questions) and topic_questions:
                st.write("You're doing amazing! Keep pushing forward!")
                st.write(
                    "Here are some explanations for the questions you answered:")
                for i, q in enumerate(topic_questions):
                    explanation = self.llm_service.get_explanation(
                        q['question'], q['answer'])
                    st.write(
                        f"**Explanation for Question {i + 1}:** {explanation}")

                    # Update the explanation in the database
                    email = st.session_state.user.get(
                        'preferred_username', 'unknown')
                    self.db_service.update_explanation(
                        username=email,
                        topic=topic,
                        question=q['question'],
                        explanation=explanation
                    )
