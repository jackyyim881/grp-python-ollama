# pages/redirect.py

import streamlit as st
from app import get_token_from_code, get_user_profile, load_cache, save_cache, get_sign_in_url

from database import DatabaseService
import datetime


def is_authenticated():
    return 'user' in st.session_state and st.session_state.user is not None


def main():
    if not is_authenticated():
        st.title("Processing Authentication...")

    if 'code' in st.query_params:
        code = st.query_params['code']
        with st.spinner('Processing...'):
            # Proceed to get the token using the code
            result = get_token_from_code(code)
            if result is not None and 'access_token' in result:
                # Successful login
                st.session_state.user = result['id_token_claims']
                st.session_state.access_token = result['access_token']
                st.session_state['token_cache'] = load_cache().serialize()
                db_service = DatabaseService()
                # Get user profile
                user_profile = get_user_profile(result['access_token'])

                username = user_profile.get('userPrincipalName', 'N/A')
                student_id = user_profile.get('id', 'N/A')
                display_name = user_profile.get('displayName', 'N/A')
                enrollment_date = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                user_in_db = db_service.get_user_by_username(username)
                if not user_in_db:
                    db_service.insert_user(username=username, student_id=student_id,
                                           display_name=display_name, enrollment_date=enrollment_date)
                    st.sidebar.write("User profile created successfully!")
                else:
                    st.sidebar.write("User profile already exists!")

                # sidebar navigation
                with st.sidebar:
                    st.page_link('app.py', label='Home', icon='🏠')

                # Save the token cache
                save_cache(load_cache())

                username = user_profile.get(
                    'displayName', 'No display name found.')
                st.empty()

                st.title(f"Welcome {username}! 🎉")

                st.success("Login successful.")

                st.page_link('app.py', label='Home', icon='🏠')

            else:
                error_description = result.get(
                    'error_description', 'No error description provided') if result else 'No result returned from token acquisition.'
                st.error(f"Login failed. {error_description}")
    else:
        with st.spinner('Redirecting to login page...'):
            st.markdown(
                f"Redirecting to the login page...")

            st.markdown(
                f"[Click here to log in with Azure AD]({get_sign_in_url()})")
        st.error("No authentication code found.")


if __name__ == "__main__":
    main()
