# pages/achievements.py

import streamlit as st
from database import DatabaseService
from datetime import datetime

from app import get_sign_in_url, generate_sidebar_links


def is_authenticated():
    """
    Check if the user is authenticated.
    """
    return 'user' in st.session_state and st.session_state.user is not None


def main():
    """
    The main function to render the achievements management page.
    """
    st.title("Achievements Management 🏆")

    # Initialize Database Service
    db_service = DatabaseService()

    # Tabs for different CRUD operations
    tab1, tab2, tab3, tab4 = st.tabs(["Create", "Read", "Update", "Delete"])

    # --- Create Achievement ---
    with tab1:
        st.header("Create a New Achievement")
        with st.form("create_achievement_form"):
            name = st.text_input("Achievement Name")
            description = st.text_area("Description")
            criteria = st.text_input("Criteria (e.g., total_correct >= 10)")
            submitted = st.form_submit_button("Create Achievement")
            if submitted:
                if name and description and criteria:
                    success = db_service.create_achievement(
                        name, description, criteria)
                    if success:
                        st.success(f"Achievement '{
                                   name}' created successfully.")
                    else:
                        st.error(
                            "Failed to create achievement. It might already exist.")
                else:
                    st.error("Please fill in all fields.")

    # --- Read Achievements ---
    with tab2:
        st.header("List of Achievements")
        achievements = db_service.read_achievements()
        if achievements:
            for ach in achievements:
                st.subheader(f"{ach[0]}: {ach[1]}")
                st.write(f"**Description:** {ach[2]}")
                st.write(f"**Criteria:** {ach[3]}")
                st.markdown("---")
        else:
            st.info("No achievements found.")

    # --- Update Achievement ---
    with tab3:
        st.header("Update an Achievement")
        achievements = db_service.read_achievements()
        achievement_names = [f"{ach[0]}: {ach[1]}" for ach in achievements]
        achievement_dict = {f"{ach[0]}: {ach[1]}": ach for ach in achievements}

        if achievements:
            selected_achievement = st.selectbox(
                "Select an achievement to update", achievement_names)
            ach = achievement_dict[selected_achievement]

            with st.form("update_achievement_form"):
                new_name = st.text_input("Achievement Name", value=ach[1])
                new_description = st.text_area("Description", value=ach[2])
                new_criteria = st.text_input("Criteria", value=ach[3])
                submitted = st.form_submit_button("Update Achievement")
                if submitted:
                    if new_name and new_description and new_criteria:
                        success = db_service.update_achievement(
                            achievement_id=ach[0],
                            name=new_name,
                            description=new_description,
                            criteria=new_criteria
                        )
                        if success:
                            st.success(f"Achievement '{
                                       new_name}' updated successfully.")
                            st.experimental_rerun()  # Refresh the page to show updates
                        else:
                            st.error("Failed to update achievement.")
                    else:
                        st.error("Please fill in all fields.")
        else:
            st.info("No achievements available to update.")

    # --- Delete Achievement ---
    with tab4:
        st.header("Delete an Achievement")
        achievements = db_service.read_achievements()
        achievement_names = [f"{ach[0]}: {ach[1]}" for ach in achievements]
        achievement_dict = {f"{ach[0]}: {ach[1]}": ach for ach in achievements}

        if achievements:
            selected_achievement = st.selectbox(
                "Select an achievement to delete", achievement_names)
            ach = achievement_dict[selected_achievement]

            if st.button("Delete Achievement"):
                success = db_service.delete_achievement(achievement_id=ach[0])
                if success:
                    st.success(f"Achievement '{ach[1]}' deleted successfully.")
                    st.experimental_rerun()  # Refresh the page to show updates
                else:
                    st.error("Failed to delete achievement.")
        else:
            st.info("No achievements available to delete.")

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
