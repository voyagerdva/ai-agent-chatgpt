# core/llm_client/base.py

from abc import ABC, abstractmethod
from core.llm_client.prompts import PROMPTS, PromptType
import asyncio
import logging

logger = logging.getLogger("ai_agent.llm.base")

class BaseLLMClient(ABC):
    def __init__(self, model: str):
        self.model = model

    @abstractmethod
    def _get_client(self):
        """Возвращает инстанс клиента конкретного провайдера (OpenAI, GigaChat и т.д.)"""
        pass

    @abstractmethod
    def _get_completion(self, messages: list):
        """Выполняет вызов API (синхронный метод, используется через asyncio.to_thread)"""
        pass

    async def send_message(self, message: str, prompt_type: PromptType = PromptType.GENERIC) -> str:
        logger.info(f"[{self.__class__.__name__}] Отправка запроса в LLM...")

        system_prompt = PROMPTS.get(prompt_type, PROMPTS[PromptType.GENERIC])

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]

        try:
            completion = await asyncio.to_thread(lambda: self._get_completion(messages))
            llm_text = completion.choices[0].message.content
            logger.info(f"[{self.__class__.__name__}] Ответ получен: {llm_text}")
            return llm_text
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка: {e}")
            return f'{{"error": "Ошибка при вызове LLM: {str(e)}"}}'
