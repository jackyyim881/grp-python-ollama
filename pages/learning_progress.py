# pages/learning_progress.py

import streamlit as st
import pandas as pd
import plotly.express as px
from database import DatabaseService
import os
import json
from PIL import Image
from io import BytesIO
from app import get_user_profile, get_user_photo
from llm_service import LLMService  # Import the LLMService
from app import get_sign_in_url, generate_sidebar_links


def is_authenticated():
    """
    Check if the user is authenticated.
    """
    return 'user' in st.session_state and st.session_state.user is not None


def add_custom_css():
    st.markdown("""
        <style>
        /* Custom styles */
        .header {
            text-align: center;
            padding: 10px;
        }
        .profile-pic {
            border-radius: 50%;
        }
        .metric-container {
            display: flex;
            justify-content: space-around;
            margin-bottom: 30px;
        }
        .metric {
            text-align: center;
        }
        .progress-table {
            margin-top: 20px;
        }
        </style>
    """, unsafe_allow_html=True)


def get_real_progress_data(db_service, username):
    """
    Fetch and process real assessment data for the user from the database.
    Returns a DataFrame with columns: Topic, Score, Total, Accuracy (%)
    """
    results = db_service.fetch_results(username)
    if not results:
        return pd.DataFrame()  # Return empty DataFrame if no results

    # Convert results to DataFrame
    df = pd.DataFrame(results, columns=[
                      'Topic', 'Question', 'User Answer', 'Correct Answer', 'Correct', 'Explanation'])

    # Group by Topic to calculate Score and Total
    progress = df.groupby('Topic').agg(
        Score=('Correct', 'sum'),
        Total=('Correct', 'count')
    ).reset_index()

    # Calculate Accuracy Percentage
    progress['Accuracy (%)'] = (progress['Score'] / progress['Total']) * 100

    return progress


def render_learning_progress():
    """
    Render the Learning Progress page content.
    """
    st.title("Your Learning Progress 📈")
    st.write("Track your learning journey with detailed metrics and visualizations.")

    # Initialize Database Service
    db_service = DatabaseService()

    # Retrieve user information from session state
    access_token = st.session_state.access_token
    user_profile = get_user_profile(access_token)
    # Assuming username is userPrincipalName
    username = user_profile.get('userPrincipalName', 'N/A')
    display_name = user_profile.get('displayName', 'User')
    email = user_profile.get('mail', 'N/A')
    student_id = user_profile.get('userPrincipalName', 'N/A')

    # Add custom CSS
    add_custom_css()

    # Header Section
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            # Fetch the profile picture
            profile_picture_data = get_user_photo(access_token)
            if profile_picture_data:
                profile_picture = Image.open(BytesIO(profile_picture_data))
                st.image(profile_picture, width=100,
                         caption="", use_container_width=False)
            else:
                # Default avatar
                st.image('data/default_avatar.png', width=100,
                         caption="", use_container_width=False)
        with col2:
            st.markdown(f"### Welcome, {display_name}!")
            st.write(f"**Email:** {email}")
            st.write(f"**Student ID:** {student_id}")

    st.markdown("---")

    # Load user progress from the database
    progress_df = get_real_progress_data(db_service, username)

    if not progress_df.empty:
        # Calculate overall metrics
        total_questions = progress_df['Total'].sum()
        total_correct = progress_df['Score'].sum()
        overall_accuracy = (total_correct / total_questions) * \
            100 if total_questions > 0 else 0
        topics_mastered = (progress_df['Accuracy (%)'] == 100).sum()

        # Display Metrics
        st.subheader("Overall Performance")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Questions Answered", int(total_questions))
        col2.metric("Overall Accuracy", f"{overall_accuracy:.2f}%")
        col3.metric("Topics Mastered", topics_mastered)

        st.markdown("---")

        # Detailed Performance Table
        st.subheader("Detailed Performance by Topic")
        st.dataframe(progress_df.style.format(
            {'Accuracy (%)': '{:.2f}%'}), height=300)

        # Visualizations
        st.subheader("Performance Visualizations")

        # Bar Chart: Accuracy per Topic
        fig_bar = px.bar(
            progress_df,
            x='Topic',
            y='Accuracy (%)',
            title='Accuracy per Topic',
            labels={'Accuracy (%)': 'Accuracy (%)'},
            color='Accuracy (%)',
            color_continuous_scale=px.colors.sequential.Blues,
            range_y=[0, 100]
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # Line Chart: Score Trend Over Topics
        # Assuming topics are ordered logically; otherwise, additional data needed for time series
        fig_line = px.line(
            progress_df,
            x='Topic',
            y='Accuracy (%)',
            title='Accuracy Over Topics',
            labels={'Accuracy (%)': 'Accuracy (%)', 'Topic': 'Topic'},
            markers=True
        )
        st.plotly_chart(fig_line, use_container_width=True)

        # Pie Chart: Correct vs Incorrect Answers
        st.subheader("Answer Distribution")
        fig_pie = px.pie(
            names=['Correct', 'Incorrect'],
            values=[total_correct, total_questions - total_correct],
            color_discrete_sequence=['#4CAF50', '#FF5252'],
            title='Correct vs Incorrect Answers'
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        # Initialize LLM Service
        llm_service = LLMService()

        # Collect performance data
        performance_data = {
            'total_answered': int(total_questions),
            'total_correct': int(total_correct),
            'topics_attempted': list(progress_df['Topic']),
            'topics_struggled': list(progress_df[progress_df['Accuracy (%)'] < 70]['Topic'])
        }

        # Add the button to get advice
        st.markdown("---")
        st.subheader("Get Personalized Advice")
        if st.button("How can I improve my exam performance?"):
            with st.spinner("Analyzing your progress and generating advice..."):
                advice = llm_service.get_encouragement(performance_data)
            st.write("### Your Personalized Advice:")
            st.write(advice)

    else:
        st.info(
            "No progress data available. Start your assessments to track your learning!")

    # Feedback Section
    st.markdown("---")
    st.subheader("Feedback and Support 💬")
    st.write("If you have any feedback or need assistance, feel free to reach out.")

    with st.form("feedback_form"):
        feedback = st.text_area("Provide your feedback or comments here:")
        submit = st.form_submit_button("Submit Feedback")

        if submit:
            if feedback.strip() == "":
                st.error("Please enter your feedback before submitting.")
            else:
                # Save feedback logic here
                # For example, you can insert the feedback into a database or send an email
                st.success("Thank you for your feedback!")

    # Close the database connection
    db_service.close()


def main():
    """
    The main function to render the Learning Progress page.
    """
    if not is_authenticated():
        st.title("Access Denied")
        st.warning("Please log in to view this page.")
        st.stop()
    with st.sidebar:
        # Only show pages if the user is logged in
        if st.session_state.get("user"):
            generate_sidebar_links()
            st.markdown('---')
        else:
            st.write("Please log in to access the application.")
            st.markdown(
                f"[Click here to log in with Azure AD]({get_sign_in_url()})")
    render_learning_progress()


if __name__ == "__main__":
    main()
