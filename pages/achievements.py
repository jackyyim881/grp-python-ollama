# achievements.py

import streamlit as st
import os
import json
from datetime import datetime
from database import DatabaseService
from PIL import Image
from app import get_sign_in_url, generate_sidebar_links
import plotly.express as px
import logging
import sqlite3

logger = logging.getLogger(__name__)


def insert_achievement(name, description, target, achieved_at=None):
    conn = sqlite3.connect('./data/assessment_records.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            target INTEGER,
            achieved_at TEXT
        )
    ''')

    cursor.execute('''
        SELECT id FROM achievements WHERE name = ?
    ''', (name,))
    if cursor.fetchone():
        logger.info(f"Achievement '{
                    name}' already exists. Skipping insertion.")
    else:
        cursor.execute('''
            INSERT INTO achievements (name, description, target, achieved_at)
            VALUES (?, ?, ?, ?)
        ''', (name, description, target, achieved_at))
        logger.info(f"Inserted achievement: {name}")

    conn.commit()
    conn.close()


time = datetime.utcnow().isoformat()

insert_achievement('First Steps', 'Answer at least 1 question',
                   1, time)
insert_achievement(
    'Quick Learner', 'Answer at least 5 questions with an accuracy of 60%', 5, time)
insert_achievement(
    'Quiz Master', 'Answer at least 10 questions correctly', 10, time)
insert_achievement(
    'Topic Explorer', 'Attempt at least 3 different topics', 3, time)


def add_custom_css():
    st.markdown("""
        <style>
        /* Custom CSS for the achievements page */
        .achievement-card {
            background-color: #ffffff;
            padding: 10px; /* Reduced padding */
            border-radius: 10px; /* Slightly smaller radius */
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); /* Smaller shadow */
            margin-bottom: 10px; /* Reduced margin */
            transition: transform 0.2s, box-shadow 0.2s; /* Faster transition */
            width: 200px; /* Fixed width */
        }
        .achievement-card:hover {
            transform: translateY(-5px); /* Smaller translate */
            box-shadow: 0 4px 8px rgba(0,0,0,0.15); /* Slightly larger shadow on hover */
        }
        .achievement-icon {
            font-size: 40px; /* Reduced icon size */
            margin-bottom: 10px; /* Reduced margin */
        }
        .locked {
            opacity: 0.6;
        }
        .metric-container {
            display: flex;
            justify-content: space-around;
            margin-bottom: 20px; /* Reduced margin */
        }
        .metric {
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)


def display_achievement(achievement, is_unlocked):
    icon = '🏆' if is_unlocked else '🔒'
    color = '#FFD700' if is_unlocked else '#A9A9A9'
    background = '#fefae0' if is_unlocked else '#ececec'
    achieved_at = f"<p><strong>Achieved At:</strong> {
        achievement['achieved_at']}</p>" if is_unlocked else ""

    st.markdown(f"""
        <div class="achievement-card" style="background-color: {background};">
            <div class="achievement-icon" style="color: {color};">{icon}</div>
            <h4>{achievement['name']}</h4> <!-- Reduced heading size -->
            <p>{achievement['description']}</p>
            <p><strong>Target:</strong> {achievement['target']}</p>
            {achieved_at}
        </div>
    """, unsafe_allow_html=True)


def evaluate_and_assign_achievements(db_service, username):
    """Evaluate user performance and assign achievements"""

    # Get user performance data
    performance = db_service.get_student_performance(username)
    if not performance:
        return False

    total_answered = performance['total_answered']
    total_correct = performance['total_correct']
    topics_attempted = performance['topics_attempted']
    topics_struggled = performance['topics_struggled']

    achievements_earned = False
    current_time = datetime.utcnow().isoformat()

    # Achievement 1: First Steps
    if total_answered >= 1:
        db_service.assign_achievement_to_user(
            username=username,
            achievement_name='First Steps',
            achieved_at=current_time
        )
        achievements_earned = True

    # Achievement 2: Quick Learner
    if total_answered >= 5 and (total_correct / total_answered) >= 0.6:
        db_service.assign_achievement_to_user(
            username=username,
            achievement_name='Quick Learner',
            achieved_at=current_time
        )
        achievements_earned = True

    # Achievement 3: Quiz Master
    if total_correct >= 10:
        db_service.assign_achievement_to_user(
            username=username,
            achievement_name='Quiz Master',
            achieved_at=current_time
        )
        achievements_earned = True

    # Achievement 4: Topic Explorer
    if len(topics_attempted) >= 3:
        db_service.assign_achievement_to_user(
            username=username,
            achievement_name='Topic Explorer',
            achieved_at=current_time
        )
        achievements_earned = True

    # Achievement 5: Master of Python
    if (total_answered >= 20 and
        (total_correct / total_answered) >= 0.9 and
            len(topics_struggled) == 0):
        db_service.assign_achievement_to_user(
            username=username,
            achievement_name='Master of Python',
            achieved_at=current_time
        )
        achievements_earned = True

    return achievements_earned


def is_authenticated():
    """
    Check if the user is authenticated.
    """
    return 'user' in st.session_state and st.session_state.user is not None


def save_feedback(username, feedback):
    """
    Save user feedback to the feedback.json file.

    Args:
        username (str): The username of the student.
        feedback (str): The feedback provided by the user.
    """
    feedback_file = 'data/feedback.json'
    feedback_data = {
        "username": username,
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


def calculate_progress(current, target):
    """
    Calculate progress percentage.

    Args:
        current (float): Current total value.
        target (float): Target value to achieve.

    Returns:
        float: Progress percentage (0 to 1).
    """
    if target == 0:
        return 0
    return min(current / target, 1.0)


def main():
    """Main function to handle authentication and render achievements page"""
    add_custom_css()

    if not is_authenticated():
        st.title("Access Denied ⚠️")
        st.warning("Please log in to view your achievements.")
        st.stop()

    # Initialize services
    db_service = DatabaseService()

    # Get user info
    user_profile = st.session_state.user
    username = user_profile.get('preferred_username') or user_profile.get(
        'email') or user_profile.get('userPrincipalName')

    # Page header
    st.title("Your Achievements 🏅")
    st.write("Track your learning journey and celebrate your progress!")

    # Get user performance
    performance = db_service.get_student_performance(username)

    # Check and assign achievements
    if evaluate_and_assign_achievements(db_service, username):
        st.success("🎉 New achievements unlocked!")
        st.balloons()

    # Display achievement cards
    user_achievements = db_service.fetch_user_achievements(username)
    achievements = db_service.fetch_all_achievements()

    # Create a set of unlocked achievement names for quick lookup
    unlocked_achievements = set(ach[0] for ach in user_achievements)

    # Display achievements
    st.markdown("---")
    st.subheader("🏆 Your Achievements")
    for idx, achievement in enumerate(achievements):

        with st.expander(f"{achievement[1]}"):
            is_unlocked = achievement[1] in unlocked_achievements
            display_achievement({
                'name': achievement[0],
                'description': achievement[1],
                'target': achievement[2],
                'achieved_at': achievement[3]
            }, is_unlocked)

        # with cols[idx]:
        #     for achievement in achievements:

        #         is_unlocked = achievement[1] in unlocked_achievements
        #         display_achievement({
        #             'name': achievement[0],
        #             'description': achievement[1],
        #             'target': achievement[2],
        #             'achieved_at': achievement[3]
        #         }, is_unlocked)  # Display the achievement card

    # Show progress stats with progress bars
    if performance:
        st.markdown("---")
        st.subheader("📊 Your Progress")
        for achievement in achievements:
            target = achievement[3]
            name = achievement[1]
            description = achievement[2]
            st.markdown(f"**{achievement[1]}**: {description}")
            st.progress(calculate_progress(
                performance['total_answered'], target))
            st.write(f"{performance['total_answered']} / {target}")
            st.write("")

    # Show feedback form
    st.markdown("---")
    with st.expander("📝 Provide Feedback"):
        feedback = st.text_area(
            "Share your thoughts about the achievements system:")
        if st.button("Submit Feedback"):
            if feedback.strip():
                save_feedback(username, feedback)
                st.success("Thank you for your feedback! 🙏")
            else:
                st.warning("Please enter some feedback before submitting.")

    # Sidebar Navigation
    with st.sidebar:
        # Only show pages if the user is logged in
        if st.session_state.get("user"):
            generate_sidebar_links()
            st.markdown('---')
        else:
            st.write("Please log in to access the application.")
            st.markdown(
                f"[Click here to log in with Azure AD]({get_sign_in_url()})")

    # Optionally, add a certificate download button
    with st.container():
        if st.button("Download Achievement Certificate"):
            # Implement certificate generation logic
            st.success("Certificate downloaded!", icon="✅")


if __name__ == "__main__":
    main()

    # Define achievements and their targets based on total_answered
    # achievements_progress = {
    #     'First Steps': {
    #         'current': performance['total_answered'],
    #         'target': 1,
    #         'description': 'Answer at least 1 question'
    #     },
    #     'Quick Learner': {
    #         'current': performance['total_answered'],
    #         'target': 5,
    #         'description': 'Answer at least 5 questions with an accuracy of 60%'
    #     },
    #     'Quiz Master': {
    #         'current': performance['total_correct'],
    #         'target': 10,
    #         'description': 'Answer at least 10 questions correctly'
    #     },
    #     'Topic Explorer': {
    #         'current': len(performance['topics_attempted']),
    #         'target': 3,
    #         'description': 'Attempt at least 3 different topics'
    #     },
    #     'Master of Python': {
    #         'current': performance['total_answered'],
    #         'target': 20,
    #         'description': 'Answer at least 20 questions with 90% accuracy and no struggled topics'
    #     }
    # }

    # for achievement_name, data in achievements[0].items():
    #     target = data['target']
    #     current = data['current']
    #     description = data['description']

    #     if achievement_name == 'Master of Python':
    #         # Special condition for Master of Python
    #         if performance['total_answered'] == 0 or performance['total_correct'] / performance['total_answered'] < 0.9 or len(performance['topics_struggled']) > 0:
    #             target = 0  # Indicate not achievable
    #             progress = 0
    #         else:
    #             progress = calculate_progress(current, target)
    #     elif achievement_name == 'Quick Learner':
    #         # Include correct rate
    #         accuracy = (performance['total_correct'] / performance['total_answered']
    #                     ) * 100 if performance['total_answered'] > 0 else 0
    #         if accuracy < 60:
    #             progress = calculate_progress(current, target)
    #         else:
    #             progress = calculate_progress(current, target)
    #     else:
    #         progress = calculate_progress(current, target)

    #     st.markdown(f"**{achievement_name}**: {description}")
    #     st.progress(progress)
    #     st.write(f"{current} / {target}")
    #     st.write("")
