# core/Controller.py

import logging
from typing import Dict, Any, List

from core.Handlers.HandlerBase import HandlerBase
from core.Handlers.HandlerFindFileInFolder import HandlerFindFileInFolder
from core.Handlers.HandlerFindTextInFiles import HandlerFindTextInFiles

from core.llm_client.LLMClientFactory import LLMClientFactory
from core.llm_client.PromptType import PromptType

from core.utils.JsonResponseExtractorByRegex import JsonResponseExtractorByRegex

logger = logging.getLogger("ai_agent.core.controller")
logger.setLevel(logging.DEBUG)

class Controller:
    def __init__(self):

        self.llm_client = LLMClientFactory.get_llm_client()
        logger.info(f"\nLLM Client initialized: {self.llm_client}\n")

        # Регистрируем обработчики
        self.handlers: List[HandlerBase] = [
            HandlerFindFileInFolder(),
            HandlerFindTextInFiles(),
        ]

        # Инициализация экстрактора JSON через regex
        self.json_extractor_regex = JsonResponseExtractorByRegex(debug=True)


    async def prepareMacroPromptAndTalkToLLM(self, message: str) -> Dict[str, Any]:
        logger.info(f"[Controller] Получен запрос: {message}")

        # Просто отправляем сообщение вместе с типом промпта MACRO_TASK
        llm_response_text = await self.llm_client.send_message(
            message,
            prompt_type=PromptType.MACRO_TASK
        )

        try:
            data = self.json_extractor_regex.extract(llm_response_text)
        except Exception as e:
            logger.error(f"[Controller] Ошибка разбора JSON: {e}")
            return {"error": f"Не удалось разобрать ответ LLM: {str(e)}"}

        actions = data.get("actions", [])
        if not actions:
            logger.error("[Controller] LLM не вернул никаких действий.")
            return {"error": "LLM не вернул никаких действий."}

        results = []
        for action in actions:
            action_type = action.get("action")  # важно: тут должно быть "action", а не "type"
            logger.info(f"[Controller] Обрабатываю действие: {action_type}")

            handler = next((h for h in self.handlers if h.can_handle(action_type)), None)
            if handler:
                result = await handler.handle(action)
                results.append(result)
            else:
                logger.warning(f"[Controller] Неподдерживаемый тип действия: {action_type}")
                results.append({
                    "action": action,
                    "result": {"error": f"Неподдерживаемый тип действия: {action_type}"}
                })

        return {"results": results}