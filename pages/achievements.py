# pages/achievements.py

import streamlit as st
import os
import json
from datetime import datetime
from database import DatabaseService
from PIL import Image


def evaluate_and_assign_achievements(db_service, username):
    performance = db_service.get_student_performance(username)
    if not performance:
        return

    total_answered = performance['total_answered']
    total_correct = performance['total_correct']
    topics_struggled = performance['topics_struggled']

    # Example: Assign "First Assessment Completed"
    if total_answered >= 1:
        db_service.assign_achievement_to_user(
            username, "First Assessment Completed", datetime.utcnow().isoformat())

    # Example: Assign "Proficient Learner"
    accuracy = (total_correct / total_answered) * \
        100 if total_answered > 0 else 0
    if accuracy >= 70:
        db_service.assign_achievement_to_user(
            username, "Proficient Learner", datetime.utcnow().isoformat())

    # Example: Assign "Mastery"
    if accuracy == 100 and not topics_struggled:
        db_service.assign_achievement_to_user(
            username, "Mastery", datetime.utcnow().isoformat())


def populate_achievements(db_service):
    achievements = [
        {
            "name": "First Assessment Completed",
            "description": "Completed your first assessment.",
            "criteria": "Completed at least one assessment."
        },
        {
            "name": "Proficient Learner",
            "description": "Achieved over 70% accuracy in assessments.",
            "criteria": "Maintain an accuracy rate above 70% across all assessments."
        },
        {
            "name": "Mastery",
            "description": "Mastered all topics with 100% accuracy.",
            "criteria": "Achieve 100% accuracy in all assessed topics."
        },
        # Add more achievements as needed
    ]

    for ach in achievements:
        db_service.add_achievement(
            ach['name'], ach['description'], ach['criteria'])


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


def save_feedback(student_id, feedback):
    """
    Save user feedback to the feedback.json file.

    Args:
        student_id (str): The ID of the student.
        feedback (str): The feedback provided by the user.
    """
    feedback_file = 'data/feedback.json'
    feedback_data = {
        "student_id": student_id,
        "feedback": feedback,
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        if os.path.exists(feedback_file):
            with open(feedback_file, 'r') as f:
                data = json.load(f)
        else:
            data = []
        data.append(feedback_data)
        with open(feedback_file, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        st.error(f"Error saving feedback: {e}")


def render_achievements():
    """
    Render the Achievements page content.
    """
    st.title("Your Achievements 🏅")
    st.write("Celebrate your milestones and track your progress.")

    # Initialize Database Service
    db_service = DatabaseService()

    # Retrieve user information from session state
    user_profile = st.session_state.user
    # Adjust based on your user identification
    student_id = user_profile.get('userPrincipalName', 'N/A')

    # Load user progress
    progress = load_progress(student_id)

    achievements = [
        {
            "name": "First Assessment Completed",
            "description": "Completed your first assessment.",
            "criteria": "Completed at least one assessment.",
            "icon": "🎉"
        },
        {
            "name": "Proficient Learner",
            "description": "Achieved over 70% accuracy in assessments.",
            "criteria": "Maintain an accuracy rate above 70% across all assessments.",
            "icon": "👍"
        },
        {
            "name": "Mastery",
            "description": "Mastered all topics with 100% accuracy.",
            "criteria": "Achieve 100% accuracy in all assessed topics.",
            "icon": "🏆"
        },
        # Add more achievements as needed
    ]

    # Define number of columns per row
    cols_per_row = 3

    # Calculate number of rows needed
    num_rows = (len(achievements) + cols_per_row - 1) // cols_per_row

    for row in range(num_rows):
        cols = st.columns(cols_per_row)
        for col_index in range(cols_per_row):
            achievement_index = row * cols_per_row + col_index
            if achievement_index < len(achievements):
                achievement = achievements[achievement_index]
                with cols[col_index]:
                    st.markdown(
                        f"""
                        <div style="
                            background-color: #f9f9f9;
                            padding: 20px;
                            border-radius: 10px;
                            text-align: center;
                            box-shadow: 2px 2px 12px rgba(0,0,0,0.1);
                            height: 100%;
                        ">
                            <h2>{achievement['icon']}</h2>
                            <h3>{achievement['name']}</h3>
                            <p>{achievement['description']}</p>
                            <small><i>Criteria: {achievement['criteria']}</i></small>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    if progress:
        # Determine achievements based on progress
        achievements = []
        for topic, data in progress.items():
            if data['score'] == data['total']:
                achievements.append(f"**Mastered {topic}** 🎉")
            elif data['score'] >= data['total'] * 0.7:
                achievements.append(f"**Proficient in {topic}** 👍")
            else:
                achievements.append(f"**Improving in {topic}** 🔄")

        if achievements:
            st.subheader("Your Achievements:")
            for achievement in achievements:
                st.write(achievement)
        else:
            st.info("Complete assessments to earn achievements!")
    else:
        st.info("No progress data available to showcase achievements.")


def main():
    """
    The main function to render the Achievements page.
    """
    if not is_authenticated():
        st.title("Access Denied")
        st.warning("Please log in to view this page.")
        st.stop()

    render_achievements()


if __name__ == "__main__":
    main()
