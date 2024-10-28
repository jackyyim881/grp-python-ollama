# main.py
import streamlit as st
from auth import AuthService, AuthProvider
from database import DatabaseService
from question_loader import QuestionLoader
from llm_service import LLMService
from ui import UIService
from config import Config


def main():
    # Initialize services
    db_service = DatabaseService()
    question_loader = QuestionLoader()
    llm_service = LLMService()

    # Determine authentication method
    auth_provider = AuthProvider(Config.USERS, db_service=db_service)
    auth_service = AuthService(auth_provider)

    # Initialize UI service with dependency injection
    ui_service = UIService(auth_service, db_service,
                           question_loader, llm_service)
    ui_service.render()

    # Ensure the database connection is closed on shutdown


if __name__ == "__main__":
    main()
