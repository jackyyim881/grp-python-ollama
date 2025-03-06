import streamlit as st
from streamlit_elements import elements, mui, html
import plotly.express as px
from database import DatabaseService
from app import get_sign_in_url, generate_sidebar_links


def main():
    # Page title and description
    st.title("Dashboard for Student Performance")
    st.write(
        "This dashboard provides an overview of student performance. You can view the total number of students, their answers, and more based on selected topics."
    )

    # Initialize the database service
    db_service = DatabaseService()

    # Fetch data
    students = db_service.get_total_student_count()
    topic = db_service.select_each_topic()
    all_students_answers = db_service.get_total_correct_answers_without_username()

    # Pie chart data for student performance (percentage of correct/incorrect answers)
    pie_data = {
        "Labels": ["Correct Answers", "Incorrect Answers"],
        "Values": [all_students_answers, students - all_students_answers]
    }

    # Create a professional Pie Chart using Plotly
    pie_fig = px.pie(
        pie_data,
        names="Labels",
        values="Values",
        title="Student Answer Performance",
        color="Labels",  # Different colors for correct/incorrect
        color_discrete_map={"Correct Answers": "#28a745",
                            "Incorrect Answers": "#dc3545"},
        template="plotly_dark"  # Dark theme for a more professional look
    )

    # Use MUI Grid layout for organizing the page into sections
    with elements("main"):
        with mui.Grid(container=True, spacing=3):
            # First section: Topic Selector and Bar Chart
            with mui.Grid(item=True, xs=12, md=8):
                selected_topic = st.selectbox(
                    "Select Topic", topic, key="topic_selector")
                st.write(f"**Selected Topic:** {selected_topic}")

            # Second section: Student Performance Pie Chart
            with mui.Grid(item=True, xs=12, md=8):
                st.markdown("### Student Performance Overview (Pie Chart)")
                st.plotly_chart(pie_fig, use_container_width=True)

            # Third section: Bar chart or any other data visualization
            with mui.Grid(item=True, xs=12, md=4):
                st.markdown("### Topic Performance")
                chart_data = {"Students": students,
                              "Correct Answers": all_students_answers}
                st.bar_chart(chart_data, height=400, use_container_width=True)

            # Spacer between sections

    # Sidebar with Login or Navigation
    with st.sidebar:
        if st.session_state.get("user"):
            generate_sidebar_links()
            st.markdown('---')
        else:
            st.write("Please log in to access the application.")
            login_link = get_sign_in_url()
            st.markdown(
                f"[Click here to log in with Azure AD]({login_link})"
            )

    # Optional: Loading spinner for better UX during data loading
    with st.spinner("Loading data..."):
        # Simulating data load or fetching process
        pass


if __name__ == "__main__":
    main()
