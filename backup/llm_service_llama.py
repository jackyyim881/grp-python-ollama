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

    Provide an encouraging message to the student that acknowledges their efforts, highlights their strengths, and offers advice on how to improve on the topics they are struggling with. Please use more emojis in your response to make it engaging and motivating. 😊🎉👍
    """
            encouragement = self.llm.invoke(prompt)
            logger.info("Fetched encouragement from LLM.")
            return encouragement.strip()
        except Exception as e:
            logger.error(f"Error fetching encouragement: {e}")
            return "Keep up the good work!"

    def chat(self, user_input):
        self.conversation_history.append(f"User: {user_input}")
        # Keep the last 6 exchanges
        conversation = "\n".join(self.conversation_history[-6:])
        prompt = f"""
You are a helpful Python programming tutor.

Maintain the following conversation with the student:

{conversation}

Assistant:
"""
        try:
            response = self.llm.invoke(prompt)
            self.conversation_history.append(f"Assistant: {response.strip()}")
            logger.info("Fetched chat response from LLM.")
            return response.strip()
        except Exception as e:
            logger.error(f"Error during chat: {e}")
            return "I'm sorry, I couldn't process your request at this time."

    def ask_question(self, student_question):
        """
        Answer a student's question.
        """
        try:
            prompt = f"You are a helpful Python tutor. Answer the following question:\n\n{
                student_question}"
            response = self.llm.invoke(prompt)
            logger.info("Fetched answer from LLM.")
            return response.strip()
        except Exception as e:
            logger.error(f"Error fetching answer: {e}")
            return "I'm sorry, I couldn't retrieve an answer at this time."
    pass

    def provide_topic_explanation(self, topic):
        """
        Provide a detailed explanation of a specific topic.
        """
        try:
            prompt = f"Explain the Python topic '{
                topic}' in detail for a beginner student."
            explanation = self.llm.invoke(prompt)
            logger.info("Fetched topic explanation from LLM.")
            return explanation.strip()
        except Exception as e:
            logger.error(f"Error fetching topic explanation: {e}")
            return "I'm sorry, I couldn't retrieve an explanation at this time."

    def generate_practice_question(self, topic):
        """
        Generate a practice question on a given topic.
        """
        try:
            prompt = f"Create a challenging practice question on the Python topic '{
                topic}', and provide the correct answer."
            practice_q_and_a = self.llm.invoke(prompt)
            logger.info("Fetched practice question from LLM.")
            return practice_q_and_a.strip()
        except Exception as e:
            logger.error(f"Error generating practice question: {e}")
            return "I'm sorry, I couldn't generate a practice question at this time."

    def offer_study_tips(self):
        """
        Offer general study tips for learning Python.
        """
        try:
            prompt = "Provide effective study tips for learning Python programming."
            study_tips = self.llm.invoke(prompt)
            logger.info("Fetched study tips from LLM.")
            return study_tips.strip()
        except Exception as e:
            logger.error(f"Error fetching study tips: {e}")
            return "I'm sorry, I couldn't retrieve study tips at this time."

    def code_review(self, code_snippet):
        """
        Review and provide feedback on a code snippet.
        """
        try:
            prompt = f"Review the following Python code snippet and provide constructive feedback:\n\n{
                code_snippet}"
            feedback = self.llm.invoke(prompt)
            logger.info("Fetched code review feedback from LLM.")
            return feedback.strip()
        except Exception as e:
            logger.error(f"Error fetching code review feedback: {e}")
            return "I'm sorry, I couldn't provide feedback at this time."
