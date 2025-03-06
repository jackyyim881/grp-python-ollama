import logging
import os
from openai import OpenAI
from config import Config
logger = logging.getLogger(__name__)


class VisionService:
    def __init__(self):
        self.client = OpenAI(api_key=Config.XAI_API_KEY,
                             base_url="https://api.x.ai/v1")
        logger.info("Initialized VisionService with OpenAI client.")

    def generate_dynamic_prompt(self, task_type, content):
        """
        This function generates a dynamic prompt based on the task type.
        :param task_type: The type of task (e.g., 'image analysis', 'student grading')
        :param content: The content to be analyzed or the user input.
        :return: A dynamic prompt string.
        """
        if task_type == 'image_analysis':
            prompt = f"Please analyze the following image and describe its content in detail: {
                content}"
        elif task_type == 'student_grading':
            prompt = f"Here is a student's work: {
                content}. Please evaluate it and provide feedback to help the student improve."
        elif task_type == 'exam_feedback':
            prompt = f"Here is a student's answer for the exam question: {
                content}. Provide a detailed explanation of any mistakes."
        else:
            prompt = f"Analyze the following and provide feedback: {content}"

        return prompt

    def invoke_image(self, task_type, content):
        """
        This method invokes the Grok Vision API with a dynamic prompt.
        :param task_type: The task for which the image content needs to be processed (e.g., grading, feedback, etc.)
        :param content: The content of the image or user input (e.g., student answers, diagrams, etc.)
        :return: The response from the API.
        """
        try:
            # Generate the dynamic prompt based on the task and content
            prompt = self.generate_dynamic_prompt(task_type, content)

            # Call the API with the dynamic prompt
            completion = self.client.chat.completions.create(
                model="grok-vision-beta",
                messages=[
                    {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."},
                    {"role": "user", "content": prompt},
                ],
            )

            # Process and return the response
            response = completion.choices[0].message.content
            logger.info("Fetched response from OpenAI.")
            return response.strip()

        except Exception as e:
            logger.error(f"Error fetching response: {e}")
            return "I'm sorry, I couldn't process your request at this time."
