import streamlit as st
from llm_service import LLMService
from app import get_sign_in_url, generate_sidebar_links
import logging

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def initialize_chat():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'selected_function' not in st.session_state:
        st.session_state.selected_function = "Chat with Assistant"


def is_authenticated():
    """
    Check if the user is authenticated.
    """
    return 'user' in st.session_state and st.session_state.user is not None


def display_chat_history():
    """
    Display the entire chat history using Streamlit's native chat components.
    """
    for chat in st.session_state.chat_history:
        sender = chat.get("sender")
        message_text = chat.get("message")

        if sender == "User":
            with st.chat_message("user"):
                st.markdown(message_text)
        elif sender == "Assistant":
            with st.chat_message("assistant"):
                st.markdown(message_text)
        else:
            logger.warning(f"Unknown sender '{sender}' in chat entry.")
            with st.chat_message("assistant"):
                st.markdown(message_text)


def clear_chat_history():
    st.session_state.chat_history = []
    st.experimental_rerun()


def handle_user_input(llm_service, user_message):
    """
    Process the user's input and generate the assistant's response.
    """
    logger.info(f"User message received: {user_message}")
    # Append user message to chat history
    st.session_state.chat_history.append(
        {"sender": "User", "message": user_message})
    display_chat_history()

    # Append a placeholder for the assistant's response
    st.session_state.chat_history.append(
        {"sender": "Assistant", "message": ""})
    assistant_index = len(st.session_state.chat_history) - 1

    # Generate assistant response
    try:
        if st.session_state.selected_function == "Ask a Question":
            response = llm_service.ask_question(user_message)
            logger.info(f"Ask a Question response: {response}")
        elif st.session_state.selected_function == "Get Topic Explanation":
            topic = user_message.replace("Explain the topic: ", "")
            response = llm_service.provide_topic_explanation(topic)
            logger.info(f"Get Topic Explanation response: {response}")
        elif st.session_state.selected_function == "Generate Practice Question":
            topic = user_message.replace(
                "Generate a practice question on: ", "")
            response = llm_service.generate_practice_question(topic)
            logger.info(f"Generate Practice Question response: {response}")
        elif st.session_state.selected_function == "Get Study Tips":
            response = llm_service.offer_study_tips()
            logger.info(f"Get Study Tips response: {response}")
        elif st.session_state.selected_function == "Code Review":
            code = user_message.replace(
                "Please review the following Python code:\n", "")
            response = llm_service.code_review(code)
            logger.info(f"Code Review response: {response}")
        elif st.session_state.selected_function == "Chat with Assistant":
            response = llm_service.chat(user_message)
            logger.info(f"Chat with Assistant response: {response}")
        else:
            response = "I'm not sure how to help with that."
            logger.warning(f"Unknown selected function: {
                           st.session_state.selected_function}")

        # Update the assistant's message in chat history
        st.session_state.chat_history[assistant_index]["message"] = response
        display_chat_history()

    except Exception as e:
        st.session_state.chat_history[assistant_index]["message"] = "Sorry, something went wrong while processing your request."
        logger.error(f"Error in handling user input: {e}")
        display_chat_history()


def main():
    """Main function to handle authentication and render chat page"""
    # Initialize chat history and selected function
    initialize_chat()

    if not is_authenticated():
        st.title("Access Denied ⚠️")
        st.warning("Please log in to use the assistant.")
        st.stop()

    llm_service = LLMService()

    # Sidebar setup
    with st.sidebar:
        if st.session_state.get("user"):
            generate_sidebar_links()
            st.markdown('---')
            if st.button("Clear Chat History"):
                clear_chat_history()
        else:
            st.write("Please log in to access the application.")
            st.markdown(
                f"[Click here to log in with Azure AD]({get_sign_in_url()})")

        # Sidebar Navigation for Assistant Functions
        st.sidebar.title("Assistant Functions")
        selected_function = st.sidebar.selectbox(
            "Choose a function",
            [
                "Chat with Assistant",
                "Ask a Question",
                "Get Topic Explanation",
                "Generate Practice Question",
                "Get Study Tips",
                "Code Review"
            ],
            index=0
        )
        st.session_state.selected_function = selected_function

    # Display chat history
    st.header(f"{st.session_state.selected_function}")
    display_chat_history()

    # Accept user input using st.chat_input
    user_message = st.chat_input(f"{st.session_state.selected_function}:")
    if user_message:
        handle_user_input(llm_service, user_message)

    # Optional: Display Debug Info
    with st.expander("🔍 Debug Info"):
        st.write("**Chat History:**", st.session_state.chat_history)
        st.write("**Selected Function:**", st.session_state.selected_function)


if __name__ == "__main__":
    main()
