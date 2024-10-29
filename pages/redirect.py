# pages/redirect.py

import streamlit as st
from app import get_token_from_code, get_user_profile, load_cache, save_cache, build_msal_app
from config import Config


def main():
    st.title("Processing authentication...")

    if 'code' in st.query_params:
        code = st.query_params['code']

        # Proceed to get the token using the code
        result = get_token_from_code(code)
        if result is not None and 'access_token' in result:
            # Successful login
            st.session_state.user = result['id_token_claims']
            st.session_state.access_token = result['access_token']

            # Clear the query parameters
            st.query_params.clear()

            st.rerun()

        else:
            error_description = result.get(
                'error_description', 'No error description provided') if result else 'No result returned from token acquisition.'
            st.error(f"Login failed. {error_description}")
    else:
        st.error("No authentication code found.")


if __name__ == "__main__":
    main()
