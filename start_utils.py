import os
import sys

from langchain_core.language_models.base import BaseLanguageModel
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from loguru import logger

logger.add(sys.stderr, colorize=True, format="<green>{time:MMMM-D-YYYY}</green> | <black>{time:HH:mm:ss}</black> | <level>{level}</level> | <cyan>{message}</cyan> | <magenta>{name}:{function}:{line}</magenta> | <yellow>{extra}</yellow>")

logger.debug("Loading environment variables from .env file")
load_dotenv()
logger.debug("Loaded environment variables from .env file")

logger.info("Loading environment variables")
APP_NAME: str = os.environ.get('APP_NAME')
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
logger.info("Loaded environment variables")

logger.info("Initializing conversation llm")
conversation_llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", google_api_key=GOOGLE_API_KEY)
rag_llm_model: BaseLanguageModel = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", google_api_key=GOOGLE_API_KEY)
logger.info("Initialised conversation llm")