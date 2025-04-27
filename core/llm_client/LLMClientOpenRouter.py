# core/llm_client/LLMClientOpenRouter.py

from openai import OpenAI
from settings.Config import Config
from core.llm_client.LLMClientBase import LLMClientBase

class LLMClientOpenRouter(LLMClientBase):
    def __init__(self):
        super().__init__(model=Config.OPENROUTER_LLM_MODEL)
        self.client = self._get_client()

    def _get_client(self):
        return OpenAI(api_key=Config.OPENROUTER_API_KEY, base_url=Config.OPENROUTER_API_BASE)

    def _get_completion(self, messages: list):
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            timeout=30
        )
