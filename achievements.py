# pages/achievements.py

import streamlit as st
import os
import json
from datetime import datetime
from database import DatabaseService
from PIL import Image
from app import get_sign_in_url, generate_sidebar_links


def add_custom_css():
    st.markdown("""
        <style>
        /* Custom CSS for the achievements page */
        .achievement-card {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            transition: transform 0.2s;
        }
        .achievement-card:hover {
            transform: translateY(-5px);
        }
        .achievement-icon {
            font-size: 50px;
            color: #FFD700;
            margin-bottom: 10px;
        }
        .locked {
            opacity: 0.5;
        }
        .metric-container {
            display: flex;
            justify-content: space-around;
            margin-bottom: 30px;
        }
        .metric {
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)


def display_achievement(achievement, is_unlocked):
    icon = '🏆' if is_unlocked else '🔒'
    locked_class = '' if is_unlocked else 'locked'
    st.markdown(f"""
        <div class="achievement-card {locked_class}">
            <div class="achievement-icon">{icon}</div>
            <h3>{achievement['name']}</h3>
            <p>{achievement['description']}</p>
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
    all_achievements = db_service.fetch_all_achievements()

    # Create a set of unlocked achievement names for quick lookup
    unlocked_achievements = set(ach[0] for ach in user_achievements)

    # Display achievements in a grid
    cols_per_row = 3
    achievements_rows = [all_achievements[i:i+cols_per_row]
                         for i in range(0, len(all_achievements), cols_per_row)]
    for row_achievements in achievements_rows:
        cols = st.columns(cols_per_row)
        for idx, achievement in enumerate(row_achievements):
            with cols[idx]:
                is_unlocked = achievement[1] in unlocked_achievements
                display_achievement({
                    'name': achievement[1],
                    'description': achievement[2]
                }, is_unlocked)

    # Show progress stats
    if performance:
        st.markdown("---")
        st.subheader("📊 Your Progress")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Questions Answered", performance['total_answered'])
        with col2:
            accuracy = (performance['total_correct'] / performance['total_answered']
                        * 100) if performance['total_answered'] > 0 else 0
            st.metric("Accuracy", f"{accuracy:.1f}%")
        with col3:
            topics_mastered = len(
                performance['topics_attempted']) - len(performance['topics_struggled'])
            st.metric("Topics Mastered", topics_mastered)

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
