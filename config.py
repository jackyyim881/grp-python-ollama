# config.py
import os
from dotenv import load_dotenv
from openai import OpenAI

# Determine the environment (development by default)
ENV = os.getenv('ENV', 'development')

# Load environment variables from the corresponding .env file
if ENV == 'production':
    load_dotenv('.env.production')
else:
    load_dotenv('.env.development')


class Config:
    ENV = ENV

    # General Settings
    APP_NAME = "PolyU SPEED Python Learning Chatbot"
    DEBUG = os.getenv('DEBUG', 'False').lower() in ['true', '1', 't']
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-default-secret-key')

    # Database Settings
    if ENV == 'development':
        DATABASE_PATH = os.getenv('DATABASE_PATH', 'assessment_records_dev.db')
    elif ENV == 'production':
        DATABASE_PATH = os.getenv(
            'DATABASE_PATH', 'assessment_records_prod.db')
    else:
        DATABASE_PATH = os.getenv('DATABASE_PATH', 'assessment_records.db')

    # Ollama LLM Settings
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2')

    # Questions File
    QUESTIONS_FILEPATH = os.getenv('QUESTIONS_FILEPATH', 'questions.json')

   # Azure AD Settings
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    TENANT_ID = os.getenv('TENANT_ID')
    AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'
    REDIRECT_PATH = os.getenv('REDIRECT_PATH', '/redirect')
    SCOPE = [os.getenv('SCOPE', 'User.Read')]

    APP_PATH = '/app'
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:8501')

    if ENV == 'production':
        BASE_URL = os.getenv('BASE_URL', 'https://yourapp.streamlit.app')
        REDIRECT_URI = os.getenv(
            'REDIRECT_URI', 'https://yourapp.streamlit.app/redirect')
        XAI_API_KEY = os.getenv('XAI_API_KEY')
    else:
        BASE_URL = os.getenv('BASE_URL', 'http://localhost:8501')
        REDIRECT_URI = os.getenv(
            'REDIRECT_URI', 'http://localhost:8501/redirect')

    XAI_API_KEY = os.getenv('XAI_API_KEY')


# Validate required configurations
required_configs = [
    'SECRET_KEY', 'DATABASE_PATH',
    'OLLAMA_BASE_URL', 'OLLAMA_MODEL',
    'QUESTIONS_FILEPATH', 'CLIENT_ID',
    'CLIENT_SECRET', 'TENANT_ID',
    'AUTHORITY', 'REDIRECT_URI', 'SCOPE', 'XAI_API_KEY'
]


missing_configs = [
    cfg for cfg in required_configs if not getattr(Config, cfg, None)]

if missing_configs:
    raise EnvironmentError(f"Missing required configuration parameters: {
                           ', '.join(missing_configs)}")
