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
        redirect_uri=f'http://localhost:8501{Config.REDIRECT_PATH}'
    )


def get_token_from_code(code):
    cache = load_cache()
    result = build_msal_app(cache=cache).acquire_token_by_authorization_code(
        code,
        scopes=Config.SCOPE,
        redirect_uri=f'http://localhost:8501{Config.REDIRECT_PATH}'
    )
    save_cache(cache)
    return result


def get_user_profile(token):
    graph_endpoint = 'https://graph.microsoft.com/v1.0/me'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(graph_endpoint, headers=headers)
    return response.json()


def main():
    st.set_page_config(page_title=Config.APP_NAME)
    st.title(Config.APP_NAME)

    if 'user' not in st.session_state:
        st.session_state.user = None

    # Handle authentication
    query_params = st.query_params

    if 'code' in query_params:
        code = query_params['code'][0]
        result = get_token_from_code(code)
        if 'access_token' in result:
            # Successful login
            db_service = DatabaseService()

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

        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.rerun()

        # Render the main UI
        ui_service.render()
    else:
        # User is not logged in, show login button
        sign_in_url = get_sign_in_url()
        st.markdown(f"[Click here to log in with Azure AD]({sign_in_url})")


if __name__ == "__main__":
    main()
