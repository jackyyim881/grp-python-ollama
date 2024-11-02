# pages/learning_progress.py

import streamlit as st
import pandas as pd
import plotly.express as px
from database import DatabaseService
import os
import json
from PIL import Image
from io import BytesIO
import requests
from app import get_user_profile, get_user_photo


def is_authenticated():
    """
    Check if the user is authenticated.
    """
    return 'user' in st.session_state and st.session_state.user is not None


def load_progress(student_id):
    """
    Load the user's learning progress from the progress.json file.

    Args:
        student_id (str): The ID of the student.

    Returns:
        dict: A dictionary containing progress data for each topic.
    """
    progress_file = 'data/progress.json'
    try:
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                progress_data = json.load(f)
            return progress_data.get(student_id, {})
        return {}
    except Exception as e:
        st.error(f"Error loading progress data: {e}")
        return {}


def render_learning_progress():
    """
    Render the Learning Progress page content.
    """
    st.title("Your Learning Progress 📈")
    st.write("Track your learning journey with detailed metrics and visualizations.")

    # Initialize Database Service
    db_service = DatabaseService()

    # Retrieve user information from session state
    user_profile = st.session_state.user
    access_token = st.session_state.access_token
    # Adjust based on your user identification
    student_id = user_profile.get('userPrincipalName', 'N/A')

    # Fetch the profile picture (optional)
    user_upn = user_profile.get(
        'mail') or user_profile.get('userPrincipalName')

    # Fetch the user's profile picture
    # Get user's profile picture
    profile_picture = get_user_photo(access_token)

    if profile_picture:
        st.image(Image.open(BytesIO(profile_picture)), width=100)

    st.write(f"Welcome, {user_profile.get('displayName', 'User')}!")

    # Load user progress
    progress = load_progress(student_id)

    if progress:
        # Convert progress data to DataFrame
        data = []
        for topic, details in progress.items():
            data.append({
                "Topic": topic,
                "Score": details.get('score', 0),
                "Total": details.get('total', 0)
            })
        df = pd.DataFrame(data)

        # Calculate additional metrics
        df['Accuracy (%)'] = (df['Score'] / df['Total']) * 100

        st.subheader("Detailed Performance")
        st.dataframe(df)

        # Bar Chart: Accuracy per Topic
        fig = px.bar(
            df,
            x='Topic',
            y='Accuracy (%)',
            title='Accuracy per Topic',
            labels={'Accuracy (%)': 'Accuracy (%)'},
            color='Accuracy (%)',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Overall Statistics
        overall_accuracy = df['Accuracy (%)'].mean()
        st.metric("Overall Accuracy", f"{overall_accuracy:.2f}%")
    else:
        st.info(
            "No progress data available. Start your assessments to track your learning!")


def main():
    """
    The main function to render the Learning Progress page.
    """
    if not is_authenticated():
        st.title("Access Denied")
        st.warning("Please log in to view this page.")
        st.stop()

    render_learning_progress()


if __name__ == "__main__":
    main()
