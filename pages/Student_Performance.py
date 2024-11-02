# pages/redirect.py

import streamlit as st
from database import DatabaseService


def main():
    st.title("Dashboard for Student Performance")

    db_service = DatabaseService()

    students = db_service.get_total_student_count()

    topic = db_service.select_each_topic()

    all_students_answers = db_service.get_total_correct_answers_without_username()

    st.selectbox("Select topic", topic)
    st.bar_chart({"students": students, "answers": all_students_answers},
                 height=400, width=700, use_container_width=False, y_label=topic)


if __name__ == "__main__":
    main()
