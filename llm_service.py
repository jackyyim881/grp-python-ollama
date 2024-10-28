# llm_service.py
from langchain_ollama import OllamaLLM
from config import Config
from logger import setup_logger

logger = setup_logger()


class LLMService:
    def __init__(self):
        self.base_url = Config.OLLAMA_BASE_URL
        self.model = Config.OLLAMA_MODEL
        try:
            self.llm = OllamaLLM(base_url=self.base_url, model=self.model)
            logger.info("Initialized LLMService.")
        except Exception as e:
            logger.error(f"Failed to initialize OllamaLLM: {e}")
            raise

    def get_explanation(self, question, answer):
        try:
            prompt = f"Explain the following question: {
                question} and its answer: {answer}"
            explanation = self.llm.invoke(prompt)
            logger.info("Fetched explanation from LLM.")
            return explanation
        except Exception as e:
            logger.error(f"Error fetching explanation: {e}")
            return "Explanation unavailable."

    def get_encouragement(self, performance_data):
        try:
            prompt = f"""
You are a supportive Python programming tutor.

Based on the student's performance data:
- Total Questions Answered: {performance_data['total_answered']}
- Total Correct Answers: {performance_data['total_correct']}
- Topics Attempted: {', '.join(performance_data['topics_attempted'])}
- Topics Struggled With: {', '.join(performance_data['topics_struggled'])}

Provide an encouraging message to the student that acknowledges their efforts, highlights their strengths, and offers advice on how to improve on the topics they are struggling with.
"""
            encouragement = self.llm.invoke(prompt)
            logger.info("Fetched encouragement from LLM.")
            return encouragement.strip()
        except Exception as e:
            logger.error(f"Error fetching encouragement: {e}")
            return "Keep up the good work!"
