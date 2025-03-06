# llm_service.py
from pydantic import BaseModel, Field, ConfigDict
import os
from openai import OpenAI
from config import Config
from logger import setup_logger
import re
import streamlit as st
from langchain_xai import ChatXAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import AIMessage

logger = setup_logger()


class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=Config.XAI_API_KEY,
                             base_url="https://api.x.ai/v1")
        self.conversation_history = []  # Initialize empty conversation history

        logger.info("Initialized LLMService with OpenAI client.")

    def invoke(self, prompt):
        try:
            completion = self.client.chat.completions.create(
                model="grok-beta",
                messages=[
                    {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhikers Guide to the Galaxy."},
                    {"role": "user", "content": prompt},
                ],
            )
            response = completion.choices[0].message.content
            logger.info("Fetched response from OpenAI.")
            return response.strip()
        except Exception as e:
            logger.error(f"Error fetching response: {e}")
            return "I'm sorry, I couldn't process your request at this time."

    def get_explanation(self, question, answer):
        try:
            prompt = f"Explain the following question: {
                question} and its answer: {answer}"
            explanation = self.invoke(prompt)
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

    Provide a brief and encouraging message to the student that acknowledges their efforts, highlights their strengths, and offers advice on how to improve on the topics they are struggling with. Keep the response concise (2-3 sentences) and use a few emojis to make it engaging and motivating. 😊🎉👍
    """
            encouragement = self.invoke(prompt)
            logger.info("Fetched encouragement from LLM.")
            return encouragement.strip()
        except Exception as e:
            logger.error(f"Error fetching encouragement: {e}")
            return "Keep up the good work! 👍"

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
            response = self.invoke(prompt)
            self.conversation_history.append(f"Assistant: {response.strip()}")
            logger.info("Fetched chat response from LLM.")
            return response.strip()
        except Exception as e:
            logger.error(f"Error during chat: {e}")
            return "I'm sorry, I couldn't process your request at this time."

    def ask_question(self, student_question):
        try:
            prompt = f"You are a helpful Python tutor. Answer the following question:\n\n{
                student_question}"
            response = self.invoke(prompt)
            logger.info("Fetched answer from LLM.")
            return response.strip()
        except Exception as e:
            logger.error(f"Error fetching answer: {e}")
            return "I'm sorry, I couldn't retrieve an answer at this time."

    def provide_topic_explanation(self, topic):
        try:
            prompt = f"Explain the Python topic '{
                topic}' in detail for a beginner student."
            explanation = self.invoke(prompt)
            logger.info("Fetched topic explanation from LLM.")
            return explanation.strip()
        except Exception as e:
            logger.error(f"Error fetching topic explanation: {e}")
            return "I'm sorry, I couldn't retrieve an explanation at this time."

    def generate_practice_question(self, topic):
        try:
            prompt = f"Create a challenging practice question on the Python topic '{
                topic}', and provide the correct answer."
            practice_q_and_a = self.invoke(prompt)
            logger.info("Fetched practice question from LLM.")
            return practice_q_and_a.strip()
        except Exception as e:
            logger.error(f"Error generating practice question: {e}")
            return "I'm sorry, I couldn't generate a practice question at this time."

    def offer_study_tips(self):
        try:
            prompt = "Provide effective study tips for learning Python programming."
            study_tips = self.invoke(prompt)
            logger.info("Fetched study tips from LLM.")
            return study_tips.strip()
        except Exception as e:
            logger.error(f"Error fetching study tips: {e}")
            return "I'm sorry, I couldn't retrieve study tips at this time."

    def code_review(self, code_snippet):
        try:
            prompt = f"Review the following Python code snippet and provide constructive feedback:\n\n{
                code_snippet}"
            feedback = self.invoke(prompt)
            logger.info("Fetched code review feedback from LLM.")
            return feedback.strip()
        except Exception as e:
            logger.error(f"Error fetching code review feedback: {e}")
            return "I'm sorry, I couldn't provide feedback at this time."


# class CodeEvaluation(BaseModel):
#     correctness: float = Field(..., ge=0, le=10)  # Score out of 10
#     efficiency: float = Field(..., ge=0, le=10)   # Score out of 10
#     code_quality: float = Field(..., ge=0, le=10)  # Score out of 10
#     overall_score: float = Field(..., ge=0, le=30)  # Total score out of 30
#     feedback: str                                  # Detailed constructive feedback
class CodeEvaluation(BaseModel):
    correctness: int
    efficiency: int
    code_quality: int
    overall_score: int
    feedback: str


class TextEvaluation(BaseModel):
    correctness: int
    feedback: str


def evaluate_with_chatxai(question, user_answer, correct_answer):
    """
    Function to evaluate user fill-in-the-blank answer using ChatXAI.

    Args:
    - question: The fill-in-the-blank question.
    - user_answer: The user's provided answer for the blank.
    - correct_answer: The correct answer to the blank.

    Returns:
    - correctness: A score (0-10) indicating how correct the user's answer is.
    - feedback: Feedback from the AI model regarding the user's answer.
    """
    try:
        # Initialize the ChatXAI model
        chat = ChatXAI(model="grok-beta", xai_api_key=Config.XAI_API_KEY)

        # Define the prompt template for answer evaluation
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are an expert at evaluating fill-in-the-blank questions. Respond with ONLY valid JSON."),
            ("user", """
            Evaluate this fill-in-the-blank question:

            QUESTION: {question}

            USER ANSWER:
            {user_answer}

            CORRECT ANSWER:
            {correct_answer}

            RESPOND WITH THIS EXACT JSON FORMAT:
            {{
                "correctness": <number 0-10>, 
                "feedback": "<feedback string>"
            }}
            NO OTHER TEXT OR FORMATTING""")
        ])

        # Format the prompt with the question, user's answer, and the correct answer
        prompt = prompt_template.format_messages(
            question=question,
            user_answer=user_answer,
            correct_answer=correct_answer
        )

        # Get the response from the AI model
        response = chat.invoke(prompt)
        logger.info(response)

        # Clean and parse the response to extract the JSON result
        content = response.content.strip()

        # Use regex to extract the JSON object from the response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found in response")

        json_str = json_match.group()

        # Clean up the JSON string (remove unwanted characters and fix formatting)
        json_str = re.sub(r'[\n\r\t]', '', json_str)
        json_str = re.sub(r',\s*}', '}', json_str)

        # Parse the cleaned JSON string into the TextEvaluation object
        evaluation = TextEvaluation.parse_raw(json_str)

        # Ensure the correctness score is within the valid range (0 to 10)
        if not (0 <= evaluation.correctness <= 10):
            raise ValueError("Invalid correctness score")

        return evaluation.correctness, evaluation.feedback

    except Exception as e:
        logger.error(f"Error during answer evaluation: {str(e)}")
        return 0, "Unable to evaluate answer. Please try again."


def evaluate_code(problem, user_code, correct_answer):
    """Evaluate user code and provide feedback."""
    try:
        # Initialize the ChatXAI model
        chat = ChatXAI(model="grok-beta", xai_api_key=Config.XAI_API_KEY)

        # Define the prompt template with strict JSON formatting
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are an expert code reviewer. Respond with ONLY valid JSON."),
            ("user", """
            Evaluate this code:
            
            PROBLEM: {problem}
            
            USER CODE:
            {user_code}
            
            CORRECT ANSWER:
            {correct_answer}
            
            RESPOND WITH THIS EXACT JSON FORMAT:
            {{
                "correctness": <number 0-10>,
                "efficiency": <number 0-10>,
                "code_quality": <number 0-10>, 
                "overall_score": <number 0-10>,
                "feedback": "<feedback string>"
            }}
            NO OTHER TEXT OR FORMATTING""")
        ])

        # Format prompt
        prompt = prompt_template.format_messages(
            problem=problem,
            user_code=user_code,
            correct_answer=correct_answer
        )

        # Get response
        response = chat.invoke(prompt)
        logger.info(response)
        # Clean response and extract JSON using simpler regex
        content = response.content.strip()
        # Find anything between first { and last }
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found in response")

        json_str = json_match.group()

        # Additional JSON cleaning
        json_str = re.sub(r'[\n\r\t]', '', json_str)
        json_str = re.sub(r',\s*}', '}', json_str)

        # Parse JSON
        evaluation = CodeEvaluation.parse_raw(json_str)

        # Validate scores are within bounds
        if not all(0 <= score <= 10 for score in [
            evaluation.correctness,
            evaluation.efficiency,
            evaluation.code_quality,
            evaluation.overall_score
        ]):
            raise ValueError("Invalid score values")

        return evaluation.overall_score, evaluation.feedback

    except Exception as e:
        logger.error(f"Error during code evaluation: {str(e)}")
        return 0, "Unable to evaluate code. Please try again."
