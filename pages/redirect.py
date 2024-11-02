# pages/redirect.py

import streamlit as st
from app import get_token_from_code, get_user_profile, load_cache, save_cache, build_msal_app, get_sign_in_url
from config import Config
import streamlit.components.v1 as components


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

                # Get user profile
                user_profile = get_user_profile(result['access_token'])

                # Save the token cache
                save_cache(load_cache())

                username = user_profile.get(
                    'displayName', 'No display name found.')
                st.empty()

                st.title(f"Welcome {username}! 🎉")

                st.success("Login successful.")
                st.markdown(
                    f'Go to app')

                st.markdown(
                    "[Click here to return to the main application](/)")

            else:
                error_description = result.get(
                    'error_description', 'No error description provided') if result else 'No result returned from token acquisition.'
                st.error(f"Login failed. {error_description}")
    else:
        st.error("No authentication code found.")


if __name__ == "__main__":
    main()
