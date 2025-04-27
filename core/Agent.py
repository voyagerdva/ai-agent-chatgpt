# core/Agent.py

import logging
import json
import re
from typing import Dict, Any, List

from core.Handlers.HandlerBase import HandlerBase
from core.Handlers.HandlerFindFileInFolder import HandlerFindFileInFolder
from core.Handlers.HandlerFindTextInFiles import HandlerFindTextInFiles

from core.llm_client.LLMClientFactory import LLMClientFactory
from core.llm_client.PromptType import PromptType
from core.llm_client.KeywordSet import KEYWORDS, KeywordSet

from core.utils.JsonResponseExtractorByRegex import JsonResponseExtractorByRegex

# from core.llm_client.gigachat import GigaChatLLMClient

logger = logging.getLogger("ai_agent.core.agent")
logger.setLevel(logging.DEBUG)

KEYWORD_TO_PROMPT_MAP = {
    KeywordSet.FIND_FILE_IN_FOLDER: PromptType.FIND_FILE_IN_FOLDER,
    KeywordSet.FIND_TEXT_IN_FILES: PromptType.FIND_TEXT_IN_FILES,
}

class Agent:
    def __init__(self):

        self.llm_client = LLMClientFactory.get_llm_client()
        print(f"\n{self.llm_client}\n")

        # Регистрируем все обработчики здесь:
        self.handlers: List[HandlerBase] = [
            HandlerFindFileInFolder(),
            HandlerFindTextInFiles(),
        ]

        # Инициализация экстрактора для регулярных выражений
        self.json_extractor_regex = JsonResponseExtractorByRegex(debug=True)

    async def preparePromptAndTalkToLLM(self, message: str) -> Dict[str, Any]:
        logger.info(f"[Agent] Получен запрос: {message}")

        prompt_type = self.get_prompt_for_message(message)
        llm_response_text = await self.llm_client.send_message(message, prompt_type=prompt_type)

        try:
            data = self.json_extractor_regex.extract(llm_response_text)
        except Exception as e:
            logger.error(f"[Agent] Ошибка разбора JSON: {e}")
            return {"error": f"Не удалось разобрать ответ LLM: {str(e)}"}

        actions = data.get("actions", [])
        if not actions:
            logger.error("[Agent] LLM не вернул никаких действий.")
            return {"error": "LLM не вернул никаких действий."}

        results = []
        for action in actions:
            action_type = action.get("type")
            logger.info(f"[Agent] Обрабатываю действие: {action_type}")

            handler = next((h for h in self.handlers if h.can_handle(action_type)), None)
            if handler:
                result = await handler.handle(action)
                results.append(result)
            else:
                logger.warning(f"[Agent] Неподдерживаемый тип действия: {action_type}")
                results.append({
                    "action": action,
                    "result": {"error": f"Неподдерживаемый тип действия: {action_type}"}
                })

        return {"results": results}

    def get_prompt_for_message(self, message: str) -> PromptType:
        msg_lower = message.lower()
        for keyword_set, patterns in KEYWORDS.items():
            if any(pattern in msg_lower for pattern in patterns):
                return KEYWORD_TO_PROMPT_MAP.get(keyword_set, PromptType.GENERIC)
        return PromptType.GENERIC


