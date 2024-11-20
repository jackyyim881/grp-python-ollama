# app.py
import streamlit as st
from config import Config
from database import DatabaseService
from question_loader import QuestionLoader
from llm_service import LLMService
from ui import UIService
import msal
import uuid
import requests
import datetime as datetime
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def load_cache():
    cache = msal.SerializableTokenCache()
    if 'token_cache' in st.session_state:
        cache.deserialize(st.session_state['token_cache'])
    return cache


def save_cache(cache):
    if cache.has_state_changed:
        st.session_state['token_cache'] = cache.serialize()


def build_msal_app(cache=None):
    return msal.ConfidentialClientApplication(
        Config.CLIENT_ID,
        authority=Config.AUTHORITY,
        client_credential=Config.CLIENT_SECRET,
        token_cache=cache
    )


def get_sign_in_url():
    return build_msal_app().get_authorization_request_url(
        scopes=Config.SCOPE,
        state=str(uuid.uuid4()),
        redirect_uri=Config.REDIRECT_URI  # 使用 Config.REDIRECT_URI
    )


def get_token_from_code(code):
    cache = load_cache()
    result = build_msal_app(cache=cache).acquire_token_by_authorization_code(
        code,
        scopes=Config.SCOPE,
        redirect_uri=Config.REDIRECT_URI  # 使用 Config.REDIRECT_URI
    )
    save_cache(cache)
    return result


def get_user_profile(token):
    graph_endpoint = 'https://graph.microsoft.com/v1.0/me'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(graph_endpoint, headers=headers)
    return response.json()


def get_user_photo(token):
    """Fetch user's profile photo from Microsoft Graph API"""
    graph_endpoint = 'https://graph.microsoft.com/v1.0/me/photo/$value'
    headers = {'Authorization': f'Bearer {token}'}

    try:
        response = requests.get(graph_endpoint, headers=headers)
        if response.status_code == 200:
            return response.content
        return None
    except Exception as e:
        logger.error(f"Error fetching user photo: {e}")
        return None


def generate_sidebar_links():
    pages_dir = os.path.join(os.path.dirname(__file__), 'pages')
    pages = [f for f in os.listdir(pages_dir) if f.endswith('.py')]

    # Optionally, define a mapping for icons or labels
    icon_mapping = {
        'app.py': '🏠',
        'Profile.py': '👤',
        'gpa.py': '🎓',
        'learning_progress.py': '📈',
        'achievements.py': '🏅',
        'management_gpa.py': '📊',
        'achievement_management.py': '📜',
        'chat.py': '💬',
        'Student_Performance.py': '📊',
        'game.py': '🎮',
        # Add more mappings as needed
    }
    st.sidebar.page_link('app.py', label='Home', icon='🏠')
    for page in pages:
        page_path = f'pages/{page}'
        page_name = page.replace('.py', '')
        label = page_name.replace('_', ' ').title()
        icon = icon_mapping.get(page, '📄')  # Default icon
        st.sidebar.page_link(page_path, label=label, icon=icon)


def display_login():
    azure_logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Microsoft_Azure.svg/225px-Microsoft_Azure.svg.png"
    sign_in_url = get_sign_in_url()

    # Markdown to display the Azure logo as a clickable link
    login_markdown = f"""
    <a href="{sign_in_url}" target="_blank">
        <img src="{azure_logo_url}" alt="Azure AD Logo" style="height:30px; vertical-align:middle;"/>
        <span style="margin-left:10px; font-size:16px; vertical-align:middle;">Click here to log in with Azure AD</span>
    </a>
    """

    # Render the HTML in Streamlit
    st.markdown(login_markdown, unsafe_allow_html=True)


def main():
    """Main function to run the Streamlit app."""

    st.set_page_config(page_title=Config.APP_NAME)
    st.title(Config.APP_NAME)

    if 'user' not in st.session_state:
        st.session_state.user = None

    if 'login_recorded' not in st.session_state:
        st.session_state.login_recorded = False

    with st.sidebar:
        # Only show pages if the user is logged in
        if st.session_state.get("user"):
            generate_sidebar_links()
            st.markdown('---')
        else:
            st.write("Please log in to access the application.")
            display_login()

    # Handle authentication
    query_params = st.query_params

    if 'code' in query_params:
        code = query_params['code'][0]
        result = get_token_from_code(code)
        if 'access_token' in result:
            # Successful login
            user_profile = get_user_profile(result['access_token'])
            st.session_state.user = user_profile  # Store user profile in session_state

            # Store access token
            st.session_state.access_token = result['access_token']

            db_service = DatabaseService()
            st.session_state.login_recorded = False  # Reset login_recorded flag

            st.query_params()
            st.rerun()
        else:
            st.error("Login failed. Please try again.")
            logger.error(f"Authentication failed: {result.get(
                'error_description', 'No error description')}")
    elif st.session_state.user:
        # User is logged in
        # Initialize services
        db_service = DatabaseService()
        question_loader = QuestionLoader()
        llm_service = LLMService()

        # Initialize UIService
        ui_service = UIService(
            db_service=db_service,
            question_loader=question_loader,
            llm_service=llm_service
        )

        # Display user information
        user_profile = get_user_profile(st.session_state.access_token)

        username = user_profile.get('displayName', 'User')

        st.sidebar.title(f"Welcome, {username}")

        login_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        st.sidebar.write(f"Login time: {login_time}")

        db_service.insert_login_time(username, login_time)

        # Get login count
        login_count = db_service.get_login_count(username)
        st.sidebar.write(f"Login count: {login_count}")

        if login_count == 0:
            st.sidebar.write(
                "Welcome to your first session! Let's get started!")
        elif login_count <= 5:
            st.sidebar.write(f"Welcome back! This is your {
                             login_count}th session. Keep up the good work!")
        else:
            st.sidebar.write(f"You're on a roll! This is your {
                             login_count}th session. Keep pushing forward!")

        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.rerun()

        ui_service.render()

    else:
        # User is not logged in, show login button
        display_login()


if __name__ == "__main__":
    main()
