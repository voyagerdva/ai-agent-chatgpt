# core/llm_client/openrouter.py

from openai import OpenAI
from settings.config import Config
from core.llm_client.base import BaseLLMClient

class OpenRouterLLMClient(BaseLLMClient):
    def __init__(self):
        super().__init__(model=Config.LLM_MODEL)
        self.client = self._get_client()

    def _get_client(self):
        return OpenAI(api_key=Config.OPENROUTER_API_KEY, base_url=Config.OPENROUTER_API_BASE)

    def _get_completion(self, messages: list):
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            timeout=30
        )
