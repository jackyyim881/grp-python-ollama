# pages/chat.py

import streamlit as st
from llm_service import LLMService
from app import get_sign_in_url, generate_sidebar_links


def is_authenticated():
    """
    Check if the user is authenticated.
    """
    return 'user' in st.session_state and st.session_state.user is not None


def main():
    st.title("Python Learning Assistant 🤖")

    if not is_authenticated():
        st.warning("Please log in to use the assistant.")
        st.stop()

    llm_service = LLMService()
    with st.sidebar:
        # Only show pages if the user is logged in
        if st.session_state.get("user"):
            generate_sidebar_links()
            st.markdown('---')
        else:
            st.write("Please log in to access the application.")
            st.markdown(
                f"[Click here to log in with Azure AD]({get_sign_in_url()})")
    st.sidebar.title("Assistant Functions")
    app_mode = st.sidebar.selectbox(
        "Choose a function",
        [
            "Ask a Question",
            "Get Topic Explanation",
            "Generate Practice Question",
            "Get Study Tips",
            "Code Review",
            "Chat with Assistant"
        ]
    )

    if app_mode == "Ask a Question":
        st.subheader("Ask a Question")
        student_question = st.text_area(
            "Enter your question about Python programming:")
        if st.button("Get Answer"):
            if student_question.strip():
                with st.spinner("Thinking..."):
                    answer = llm_service.ask_question(student_question)
                st.write("### Answer:")
                st.write(answer)
            else:
                st.warning("Please enter a question.")

    elif app_mode == "Get Topic Explanation":
        st.subheader("Get Topic Explanation")
        topic = st.text_input("Enter a Python topic you want to learn about:")
        if st.button("Explain Topic"):
            if topic.strip():
                with st.spinner("Generating explanation..."):
                    explanation = llm_service.provide_topic_explanation(topic)
                st.write("### Explanation:")
                st.write(explanation)
            else:
                st.warning("Please enter a topic.")

    elif app_mode == "Generate Practice Question":
        st.subheader("Generate Practice Question")
        practice_topic = st.text_input(
            "Enter a topic for a practice question:")
        if st.button("Generate Question"):
            if practice_topic.strip():
                with st.spinner("Creating practice question..."):
                    practice_q_and_a = llm_service.generate_practice_question(
                        practice_topic)
                st.write("### Practice Question and Answer:")
                st.write(practice_q_and_a)
            else:
                st.warning("Please enter a topic.")

    elif app_mode == "Get Study Tips":
        st.subheader("Study Tips")
        if st.button("Get Study Tips"):
            with st.spinner("Fetching study tips..."):
                tips = llm_service.offer_study_tips()
            st.write("### Study Tips:")
            st.write(tips)

    elif app_mode == "Code Review":
        st.subheader("Code Review")
        code_snippet = st.text_area("Paste your Python code here:")
        if st.button("Review Code"):
            if code_snippet.strip():
                with st.spinner("Reviewing code..."):
                    feedback = llm_service.code_review(code_snippet)
                st.write("### Code Review:")
                st.write(feedback)
            else:
                st.warning("Please enter your code.")

    elif app_mode == "Chat with Assistant":
        st.subheader("Chat with the Python Tutor")

        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        user_message = st.text_input("You:", key="chat_input")
        if st.button("Send", key="send_button"):
            if user_message.strip():
                with st.spinner("Assistant is typing..."):
                    response = llm_service.chat(user_message)
                # Update chat history
                st.session_state.chat_history.append(("You", user_message))
                st.session_state.chat_history.append(("Assistant", response))
                # Display chat history
                for sender, message in st.session_state.chat_history:
                    st.markdown(f"**{sender}:** {message}")
                # Clear input
                st.session_state.chat_input = ""
            else:
                st.warning("Please enter a message.")
        else:
            # Display chat history if available
            if st.session_state.chat_history:
                for sender, message in st.session_state.chat_history:
                    st.markdown(f"**{sender}:** {message}")


if __name__ == "__main__":
    main()
