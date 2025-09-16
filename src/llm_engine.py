
import logging
import os
from typing import Optional

from langchain.prompts import ChatPromptTemplate
from config import chat_configuration

from src.custom_modules.custom_chatmodel import CustomChatModel


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def create_prompt_template(message: str) -> ChatPromptTemplate:
    """Create a ChatPromptTemplate from a human message."""
    return ChatPromptTemplate.from_messages([("human", message)])


def create_llm(model: Optional[str] = None) -> CustomChatModel:
    llm = CustomChatModel(
        openai_api_key=os.getenv("GITHUB_TOKEN"),
        openai_api_base=chat_configuration["endpoint"],
        model_name=model or chat_configuration["model"],
    )
    logger.info(f'LMM created with model: {llm.model_name}')
    return llm
