import logging
import os
import requests
from typing import List, Optional, Dict, Any

from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langchain.chat_models.base import BaseChatModel
from langchain.schema import (
    AIMessage, ChatMessage, ChatGeneration, ChatResult, BaseMessage
)
from src.config import chat_configuration

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class CustomChatModel(BaseChatModel, Runnable):
    openai_api_key: str
    openai_api_base: str
    model_name: str

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        config: Optional[RunnableConfig] = None,
    ) -> ChatResult:
        """Generate a chat response from GitHub AI endpoint."""
        chat_messages = [
            {"role": m.type if isinstance(m, ChatMessage) else "user", "content": m.content}
            for m in messages
        ]

        body: Dict[str, Any] = {
            "model": self.model_name,
            "messages": chat_messages,
        }
        if config:
            body.update(config)

        headers = {"Authorization": f"Bearer {self.openai_api_key}"}

        response = requests.post(self.openai_api_base, headers=headers, json=body)
        response.raise_for_status()  # raise exception if request fails

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        ai_message = AIMessage(content=content)
        return ChatResult(generations=[ChatGeneration(message=ai_message)])

    def _llm_type(self) -> str:
        return "github-openai"

    @classmethod
    def create_prompt_template(cls, message: str) -> ChatPromptTemplate:
        """Create a ChatPromptTemplate from a human message."""
        return ChatPromptTemplate.from_messages([("human", message)])

    @classmethod
    def from_config(cls) -> "CustomChatModel":
        """Factory method to create the model from config/env vars."""
        logger.info(f'Creating LLM with model: {chat_configuration["model"]}')
        return cls(
            openai_api_key=os.getenv("GITHUB_TOKEN"),
            openai_api_base=chat_configuration["endpoint"],
            model_name=chat_configuration["model"],
        )
