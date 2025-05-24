#=== core/llm_client/LLMClientBase.py ===============

from abc import ABC, abstractmethod

from core.llm_client.SystemPromptType import SYSTEM_PROMPTS, SystemPromptType
import asyncio
import logging
from core.SessionContext import SessionContext

logger = logging.getLogger("ai_agent.llm.base")

class LLMClientBase(ABC):
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

    async def send_message(self, session: SessionContext, user_message: str, prompt_type: SystemPromptType) -> str:
        logger.info(
            f"[{self.__class__.__name__}] Отправка запроса в LLM (session_id={session.get_id()}, turn={session.turn_count + 1})...")

        # Добавим system prompt на первом ходу
        if session.turn_count == 0:
            system_prompt = SYSTEM_PROMPTS.get(prompt_type)
            session.add_message("system", system_prompt)

        session.add_message("user", user_message)
        messages = session.get_history()

        try:
            # == РЕАЛЬНЫЙ ВЫЗОВ LLM ==
            completion = await asyncio.to_thread(lambda: self._get_completion(messages))
            llm_text = completion.choices[0].message.content

            logger.info(f"\n[{self.__class__.__name__}] Ответ получен:\n{llm_text}\n")
            session.add_message("assistant", llm_text)

            return llm_text
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка: {e}")
            return f'{{"error": "Ошибка при вызове LLM: {str(e)}"}}'

