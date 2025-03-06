import streamlit as st
from app import get_sign_in_url, generate_sidebar_links
# Assuming the VisionService class is imported from vision_service.py
from vision_service import VisionService

# Main Content - Task actions will be displayed in the main area


def main_content():
    st.header("Actions")

    task_type = st.radio("Choose Task Type", [
                         'Image Analysis', 'Grading Feedback', 'Exam Feedback'])

    if task_type == 'Image Analysis':
        st.subheader("Upload Your Image")
        image_file = st.file_uploader("Upload an Image", type=[
                                      "jpg", "jpeg", "png", "gif"])
        if image_file is not None:
            st.image(image_file, caption='Uploaded Image',
                     use_column_width=True)
            # Invoke the image analysis using the VisionService
            vision_service = VisionService()
            image_analysis_result = vision_service.invoke_image(
                'image_analysis', image_file)
            st.subheader("Analysis Result")
            st.write(image_analysis_result)

    elif task_type == 'Grading Feedback':
        st.subheader("Enter Your Text or Code for Feedback")
        student_input = st.text_area("Paste Your Work Here", height=200)
        if student_input:
            st.write("Processing your feedback...")

    elif task_type == 'Exam Feedback':
        st.subheader("Upload Your Exam Paper")
        exam_file = st.file_uploader(
            "Upload Your Exam Paper", type=["pdf", "docx", "txt"])
        if exam_file is not None:
            st.write("Exam paper uploaded. Now processing...")

    # Buttons for processing the task
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Submit Task"):
            st.write(f"Processing {task_type}...")
    with col2:
        if st.button("Clear Task"):
            st.write("Task cleared.")

# Main application function


def main():
    st.title("AI-Powered Student Performance Feedback System")
    st.write("""
    This system allows students to upload their work, receive feedback, and improve their grades through AI-powered analysis.
    """)

    with st.sidebar:
        # Only show pages if the user is logged in
        if st.session_state.get("user"):
            generate_sidebar_links()
            st.markdown('---')
        else:
            st.write("Please log in to access the application.")
            st.markdown(
                f"[Click here to log in with Azure AD]({get_sign_in_url()})")

    # Display the main content
    main_content()


if __name__ == "__main__":
    main()
