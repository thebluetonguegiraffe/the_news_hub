
import logging
import os

from langchain.prompts import ChatPromptTemplate
from config import chat_configuration

from src.custom_modules.custom_chatmodel import CustomChatModel


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def create_prompt_template(message: str) -> ChatPromptTemplate:
    """Create a ChatPromptTemplate from a human message."""
    return ChatPromptTemplate.from_messages([("human", message)])


def create_llm():
    logger.info(f'LMM created with model: {chat_configuration["model"]}')
    llm = CustomChatModel(
        openai_api_key=os.getenv("GITHUB_TOKEN"),
        openai_api_base=chat_configuration["endpoint"],
        model_name=chat_configuration["model"],
    )
    return llm
