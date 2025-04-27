# core/llm_client/LLMClientGigaChat .py

from gigachat import GigaChat  # или другой клиент
from settings.Config import Config
from core.llm_client.LLMClientBase import LLMClientBase

class LLMClientGigaChat(LLMClientBase):
    def __init__(self):
        super().__init__(model=Config.GIGACHAT_MODEL)
        self.client = self._get_client()

    def _get_client(self):
        return GigaChat(token=Config.GIGACHAT_TOKEN, base_url=Config.GIGACHAT_BASE_URL)

    def _get_completion(self, messages: list):
        return self.client.chat(messages=messages, model=self.model)
