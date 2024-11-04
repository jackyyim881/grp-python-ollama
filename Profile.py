# pages/profile.py

import streamlit as st
import json
import os
from PIL import Image
import plotly.express as px
from database import DatabaseService
from datetime import datetime
from database import DatabaseService
from app import get_user_profile, get_user_photo, get_sign_in_url, generate_sidebar_links
st.set_page_config(page_title="Profile")


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


def download_progress(progress, student_id):
    """
    Allow users to download their progress as a CSV file.

    Args:
        progress (dict): The user's progress data.
        student_id (str): The ID of the student.
    """
    import pandas as pd
    if progress:
        data = []
        for topic, details in progress.items():
            data.append({
                "Topic": topic,
                "Score": details.get('score', 0),
                "Total": details.get('total', 0)
            })
        df = pd.DataFrame(data)
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Progress as CSV",
            data=csv,
            file_name=f'{student_id}_progress.csv',
            mime='text/csv',
        )
    else:
        st.info("No progress data to download.")


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


def add_custom_css():
    """
    Inject custom CSS to enhance the aesthetics of the profile page.
    """
    custom_css = """
    <style>
    .reportview-container {
        background: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background: #ffffff;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def main():
    """
    The main function to render the profile page.
    """
    add_custom_css()

    # Check if the user is authenticated
    if not is_authenticated():
        st.title("Access Denied")
        st.warning("Please log in to view your profile.")
        st.stop()

    st.title("Your Profile 📋")

    # Retrieve user information from session state
    user = st.session_state.user
    access_token = st.session_state.access_token

    # Fetch additional user details
    user_profile = get_user_profile(access_token)
    username = user_profile.get('userPrincipalName', 'User')
    with st.sidebar:
        # Only show pages if the user is logged in
        if st.session_state.get("user"):
            generate_sidebar_links()
            st.markdown('---')
        else:
            st.write("Please log in to access the application.")
            st.markdown(
                f"[Click here to log in with Azure AD]({get_sign_in_url()})")

    # Initialize Database Service
    db_service = DatabaseService()

    # Now that 'username' is defined, you can use it
    user_in_db = db_service.get_user_by_username(username)

    if user_in_db:
        enrollment_date = user_in_db[4]
        student_id = user_in_db[1]
    else:
        enrollment_date = 'N/A'
        student_id = 'N/A'

    st.write(f"Welcome, {username}!")

    # Layout: Use columns for better organization
    col1, col2 = st.columns([1, 2])

    with col1:
        # Try to fetch and display user's profile photo
        photo_data = get_user_photo(access_token)

        if photo_data:
            # Display the photo from binary data
            from io import BytesIO
            image = Image.open(BytesIO(photo_data))
            st.image(image, width=150, caption="Profile Picture")
        else:
            # Fall back to default avatar
            avatar_path = 'data/default_avatar.png'
            if os.path.exists(avatar_path):
                avatar = Image.open(avatar_path)
            else:
                # Create dummy image if no avatar is available
                avatar = Image.new('RGB', (150, 150), color=(73, 109, 137))
            st.image(avatar, width=150, caption="Profile Picture")

    with col2:
        # Display user details
        st.subheader(f"Name: {user_profile.get('displayName', 'N/A')}")
        st.write(f"**Email:** {user_profile.get('mail', 'N/A')}")
        st.write(f"**Student ID:** {student_id}")
        st.write(f"**Enrollment Date:** {enrollment_date}")

    st.markdown("---")

    # Progress Section
    st.header("Your Learning Progress 📈")

    # Load user progress
    student_id = st.session_state.get('student_id', '')
    progress = load_progress(student_id)

    if progress:
        # Extract data for visualization
        topics = list(progress.keys())
        scores = [progress[topic]['score'] for topic in topics]
        total_questions = [progress[topic]['total'] for topic in topics]

        # Bar Chart: Correct Answers per Topic
        fig = px.bar(
            x=topics,
            y=scores,
            labels={'x': 'Topics', 'y': 'Correct Answers'},
            title="Performance per Topic",
            text=scores,
            color=topics,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        st.plotly_chart(fig, use_container_width=True)

        # Donut Chart: Overall Accuracy
        total_correct = sum(scores)
        total_questions_sum = sum(total_questions)
        overall_accuracy = (total_correct / total_questions_sum) * \
            100 if total_questions_sum > 0 else 0

        fig_donut = px.pie(
            names=["Correct", "Incorrect"],
            values=[total_correct, total_questions_sum - total_correct],
            hole=0.4,
            title=f"Overall Accuracy: {overall_accuracy:.2f}%",
            color=["Correct", "Incorrect"],
            color_discrete_sequence=["#4CAF50", "#FF5252"]
        )
        st.plotly_chart(fig_donut, use_container_width=True)

        # Download Progress
        download_progress(progress, student_id)
    else:
        st.info(
            "No progress data available. Start your assessments to track your learning!")

    st.markdown("---")

    # Achievements Section
    st.header("Your Achievements 🏅")

    # Display badges based on progress
    achievements = []
    if progress:
        for topic, data in progress.items():
            if data['score'] == data['total']:
                achievements.append(f"**Mastered {topic}** 🎉")
            elif data['score'] >= data['total'] * 0.7:
                achievements.append(f"**Proficient in {topic}** 👍")
            else:
                achievements.append(f"**Improving in {topic}** 🔄")

    if achievements:
        for achievement in achievements:
            st.write(achievement)
    else:
        st.info("Complete assessments to earn achievements!")

    st.markdown("---")

    # Feedback Section
    st.header("Feedback and Support 💬")
    st.write("If you have any feedback or need assistance, feel free to reach out through the **Chatbot** section.")

    # Feedback Form
    with st.form("feedback_form"):
        feedback = st.text_area("Provide your feedback or comments here:")
        submit = st.form_submit_button("Submit Feedback")

        if submit:
            if feedback.strip() == "":
                st.error("Please enter your feedback before submitting.")
            else:
                save_feedback(student_id, feedback)
                st.success("Thank you for your feedback!")

    # Footer
    st.markdown("---")
    st.markdown(
        "© 2024 PolyU SPEED Python Learning Chatbot. All rights reserved.")


if __name__ == "__main__":
    main()
