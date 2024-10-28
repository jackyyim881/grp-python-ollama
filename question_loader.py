# question_loader.py
import json
import os
import streamlit as st
from config import Config


@st.cache_data(ttl=3600, show_spinner=False)
def load_questions_cached(filepath):
    """
    Loads questions from a JSON file with caching.

    Args:
        filepath (str): Path to the JSON file containing questions.

    Returns:
        dict: Dictionary of questions.
    """
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            questions = json.load(file)
            st.success("Questions loaded successfully.")
            return questions
    else:
        st.error(f"Questions file not found at {filepath}.")
        return {}


class QuestionLoader:
    def __init__(self):
        self.filepath = Config.QUESTIONS_FILEPATH

    def load_questions(self):
        """
        Loads questions using the cached function.

        Returns:
            dict: Dictionary of questions.
        """
        return load_questions_cached(self.filepath)
