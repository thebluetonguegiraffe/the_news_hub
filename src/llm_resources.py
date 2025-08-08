

import os
from langchain.prompts import ChatPromptTemplate

from src.config import chat_configuration
from github_ai_chat_model.github_AI_chat import GitHubAIChatModel

class LLMResources:

    @staticmethod
    def create_prompt_template(message: str):
        message = message
        prompt_template = ChatPromptTemplate.from_messages([("human", message)])
        return prompt_template

    @staticmethod
    def create_llm():
        llm = GitHubAIChatModel(
            openai_api_key=os.getenv("GITHUB_TOKEN"),
            openai_api_base=chat_configuration["endpoint"],
            model_name=chat_configuration["model"],
        )
        return llm