# pages/redirect.py

import streamlit as st
from database import DatabaseService
from app import get_sign_in_url, generate_sidebar_links


def main():
    st.title("Dashboard for Student Performance")

    db_service = DatabaseService()

    students = db_service.get_total_student_count()

    topic = db_service.select_each_topic()

    all_students_answers = db_service.get_total_correct_answers_without_username()

    st.selectbox("Select topic", topic)
    st.bar_chart({"students": students, "answers": all_students_answers},
                 height=400, width=700, use_container_width=False, y_label=topic)

    with st.sidebar:
        # Only show pages if the user is logged in
        if st.session_state.get("user"):
            generate_sidebar_links()
            st.markdown('---')
        else:
            st.write("Please log in to access the application.")
            st.markdown(
                f"[Click here to log in with Azure AD]({get_sign_in_url()})")


if __name__ == "__main__":
    main()
