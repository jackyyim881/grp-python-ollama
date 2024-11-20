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

        # Existing encouragement messages (can be retained or removed if relying solely on LLM)
        self.encouragement_messages_correct = [
            "Excellent work! 🎉",
            "Fantastic job! 🌟",
            "You're on fire! 🔥",
            "Keep up the great effort! 👍",
            "You're mastering this topic! 📚"
        ]

        self.encouragement_messages_incorrect = [
            "Don't worry, you'll get it next time! 😊",
            "Keep trying, practice makes perfect! 💪",
            "Stay positive, you'll improve! 🌈",
            "Review the material and try again! 📖",
            "Don't give up! 🚀"
        ]

        # Define available topics
        self.available_topics = ["Set", "Tuple", "Anonymous Function"]

    def render(self):
        """
        Render the main UI of the application.
        """
        self.sidebar_menu()

        # Fetch user email correctly
        email = st.session_state.user.get('preferred_username') or st.session_state.user.get(
            'email') or st.session_state.user.get('userPrincipalName') or 'unknown'

        username = st.session_state.user.get('displayName') or 'User'

        if email == 'unknown':
            st.error("Unable to determine user email. Please contact support.")
            return

        # Initialize performance data in session if not present
        if 'performance_data' not in st.session_state:
            st.session_state.performance_data = self.db_service.get_student_performance(
                email)

        # Display performance summary
        self.display_performance_summary(email, username)

        # Display sidebar menu and main content
        if st.session_state.get('view_results', False):
            self.show_results()
        else:
            self.show_questions()

    def sidebar_menu(self):
        st.sidebar.success("You are logged in! ✅")
        st.sidebar.write("Keep up the good work! You are doing great! 💪🌟")

        if 'view_results' not in st.session_state:
            st.session_state.view_results = False

        if st.sidebar.button("View Assessment Results"):
            st.session_state.view_results = True
        elif st.sidebar.button("Answer Questions"):
            st.session_state.view_results = False

    def display_performance_summary(self, email, username):
        """
        Display the user's performance summary in the sidebar.
        """
        login_count = self.db_service.get_login_count(username)
        total_questions_answered = self.db_service.get_total_questions_answered(
            email)
        total_correct_answers = self.db_service.get_total_correct_answers(
            email)

        if total_questions_answered == 0:
            st.sidebar.write(
                "You haven't answered any questions yet. Let's dive in! 🌊📚")
        else:
            st.sidebar.write(f"You've answered {total_questions_answered} questions with {
                             total_correct_answers} correct answers. Keep it up! 👍✨")

    def show_results(self):
        st.subheader("Assessment Results 📊")
        email = st.session_state.user.get('preferred_username') or st.session_state.user.get(
            'email') or st.session_state.user.get('userPrincipalName') or 'unknown'
        results = self.db_service.fetch_results(email)
        if results:
            correct_count = sum(result[4] for result in results)
            total = len(results)
            st.write(f"You answered {correct_count} out of {
                     total} questions correctly. 🎯✅")
            for result in results:
                st.write(f"**Topic:** {result[0]} 📌")
                st.write(f"**Question:** {result[1]} ❓")
                st.write(f"**Your Answer:** {result[2]} ✍️")
                st.write(f"**Correct Answer:** {result[3]} 🏆")
                st.write(f"**Correct:** {'Yes ✅' if result[4] else 'No ❌'}")
                # Assuming explanations include emojis
                st.markdown(f"**Explanation:** {result[5]}")
                st.write("---")
            if st.sidebar.button("Show Correct Answers Summary with Graph 📈"):
                self.show_summary_graph(results)
        else:
            st.write("No assessment results found. 🤔")

    def show_summary_graph(self, results):
        correct_answers_count = sum(result[4] for result in results)
        total_answers_count = len(results)

        with elements('correct_answers_summary'):
            mui.Box(
                sx={"padding": "16px", "maxWidth": "400px", "margin": "auto"},
                children=[
                    mui.Typography(variant="h5", gutterBottom=True,
                                   children="Summary of Correct vs Incorrect Answers 📊"),
                    mui.Typography(variant="subtitle1", gutterBottom=True,
                                   children=f"Total Questions: {total_answers_count} 📝"),
                    mui.Typography(variant="subtitle1", gutterBottom=True,
                                   children=f"Correct Answers: {correct_answers_count} ✅"),
                    mui.LinearProgress(variant="determinate", value=(
                        correct_answers_count / total_answers_count) * 100, color="primary")
                ]
            )

    def show_questions(self):
        st.subheader("Python Self-Assessment 🐍📚")

        email = st.session_state.user.get('preferred_username') or st.session_state.user.get(
            'email') or st.session_state.user.get('userPrincipalName') or 'unknown'

        if email == 'unknown':
            st.error("Unable to determine user email. Please contact support.")
            return

        # Initialize question tracking in session state
        if 'current_topic' not in st.session_state:
            st.session_state.current_topic = None
        if 'current_question_index' not in st.session_state:
            st.session_state.current_question_index = 0
        if 'submitted_questions' not in st.session_state:
            st.session_state.submitted_questions = set()
        if 'show_encouragement' not in st.session_state:
            st.session_state.show_encouragement = False

        # If no topic selected, prompt user to select one
        if not st.session_state.current_topic:
            st.write("Select a Python topic to begin your assessment.")
            topic = st.selectbox("Choose a topic:", self.available_topics)
            if st.button("Start Assessment"):
                st.session_state.current_topic = topic
                st.session_state.current_question_index = 0
                st.session_state.submitted_questions = set()
                st.rerun()
        else:
            topic = st.session_state.current_topic
            st.write(f"You have selected: **{topic}** ✅")
            st.write("Let's get started with the assessment! 🚀")

            topic_questions = self.question_loader.load_questions().get(topic, [])
            total_questions = len(topic_questions)

            if st.session_state.current_question_index < total_questions:
                current_q = topic_questions[st.session_state.current_question_index]
                q_number = st.session_state.current_question_index + 1

                st.write(f"**Question {q_number}:** {current_q['question']} ❓")
                answer = st.radio("Select an answer:",
                                  current_q['options'], key=f"q_{q_number}")

                if not st.session_state.show_encouragement:
                    if st.button(f"Submit Answer for Question {q_number}", key=f"submit_{q_number}"):
                        correct = 1 if answer == current_q['answer'] else 0
                        if correct:
                            st.success("Correct! Excellent job!")
                            message_type = "success"
                        else:
                            st.error(
                                "That's not correct. Don't worry, you can try again!")
                            message_type = "error"

                        # Store the result
                        self.db_service.insert_result(
                            username=email,
                            topic=topic,
                            question=current_q['question'],
                            user_answer=answer,
                            correct_answer=current_q['answer'],
                            correct=correct,
                            explanation=""  # Will be updated later
                        )

                        # Update performance data
                        st.session_state.performance_data = self.db_service.get_student_performance(
                            email)

                        # Fetch encouragement from LLM
                        encouragement = self.llm_service.get_encouragement(
                            st.session_state.performance_data)

                        # Update the explanation in the database
                        self.db_service.update_explanation(
                            username=email,
                            topic=topic,
                            question=current_q['question'],
                            explanation=encouragement
                        )

                        # Store encouragement in session state
                        st.session_state.current_encouragement = encouragement
                        st.session_state.show_encouragement = True

                        # Display encouragement
                        self.show_encouragement_message(
                            encouragement, success=bool(correct))

                if st.session_state.show_encouragement:
                    if st.button("Next Question"):
                        st.session_state.show_encouragement = False
                        st.session_state.current_question_index += 1
                        st.rerun()

            else:
                st.write("You've completed all questions for this topic! 🎉")
                st.write("Great job! Here's your performance summary:")
                correct_answers = self.db_service.get_total_correct_answers(
                    email)
                total_answered = self.db_service.get_total_questions_answered(
                    email)
                st.write(f"**Total Questions Answered:** {total_answered} 📝")
                st.write(f"**Total Correct Answers:** {correct_answers} ✅")

                # Suggest next topic
                next_topic = self.suggest_next_topic(current_topic=topic)
                if next_topic:
                    st.write(
                        f"Would you like to **study {next_topic}** next? 📚")
                    if st.button(f"Start {next_topic} Assessment"):
                        st.session_state.current_topic = next_topic
                        st.session_state.current_question_index = 0
                        st.session_state.submitted_questions = set()
                        st.session_state.show_encouragement = False
                        st.rerun()
                else:
                    st.write(
                        "You've completed all available topics! 🎉 Keep up the great work! 🚀")

    def show_encouragement_message(self, message, success=True):
        """
        Display a professional encouragement message using MUI Alert.
        """
        with elements("encouragement_message"):
            mui.Alert(
                severity="success" if success else "info",
                children=message,
                sx={
                    "margin": "20px 0",
                    "padding": "10px",
                    "borderRadius": "5px",
                    "fontSize": "16px",
                },
            )

    def suggest_next_topic(self, current_topic):
        """
        Suggest the next topic based on available topics.
        """
        topics = self.available_topics.copy()
        if current_topic in topics:
            topics.remove(current_topic)
        if topics:
            return random.choice(topics)
        return None
