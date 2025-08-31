import json
import logging
import time
import requests
from typing import List, Optional, Dict, Any

from langchain_core.runnables import Runnable, RunnableConfig
from langchain.chat_models.base import BaseChatModel
from langchain.schema import AIMessage, ChatMessage, ChatGeneration, ChatResult, BaseMessage

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class CustomChatModel(BaseChatModel, Runnable):
    openai_api_key: str
    openai_api_base: str
    model_name: str
    last_request_time: float = 0  # Fixed the asterisks
    min_request_interval: float = 10.0  # Minimum seconds between requests
    max_retries: int = 10  # Maximum retry attempts
    retry_delay: float = 5.0  # Base delay for exponential backoff
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        config: Optional[RunnableConfig] = None,
    ) -> ChatResult:
        """Generate a chat response from GitHub AI endpoint."""

        # Rate limiting: ensure minimum time between requests
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        # Update last request time
        self.last_request_time = time.time()

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

        # Retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url=self.openai_api_base,
                    headers=headers,
                    json=body,
                    timeout=30  # Add timeout
                )
                response.raise_for_status()
                break  # Success, exit retry loop
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit error
                    if attempt < self.max_retries - 1:  # Not the last attempt
                        wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                        logger.info(f"Rate limit hit (429). Retrying in {wait_time} seconds... (attempt {attempt + 1}/{self.max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"Rate limit exceeded after {self.max_retries} attempts") from e
                elif e.response.status_code == 400:  
                    logger.info(f"Bad request: {e.response.text}")
                    error_text = e.response.text
                    error_dict = json.loads(error_text)
                    error = error_dict.get('error', {}).get("innererror", {}).get("code", "")
                    if error == "ResponsibleAIPolicyViolation":
                        logger.info(f"ResponsibleAIPolicyViolation error. Query skiped")
                        return ChatResult(generations=[ChatGeneration(message=AIMessage(content="NO_TOPIC"))])
                    else:
                        break
                else:
                    raise  # Re-raise non-rate-limit errors immediately
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.info(f"Request failed: {e}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise
        data = response.json()
        content = data["choices"][0]["message"]["content"]

        ai_message = AIMessage(content=content)
        return ChatResult(generations=[ChatGeneration(message=ai_message)])

    def _llm_type(self) -> str:
        return "github-openai"
