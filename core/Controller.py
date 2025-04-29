# core/Controller.py

import logging
from typing import Dict, Any, List

from core.Handlers.HandlerBase import HandlerBase
from core.Handlers.HandlerFindFileByPrefix import HandlerFindFileByPrefix
from core.Handlers.HandlerFindTextInFiles import HandlerFindTextInFiles

from core.llm_client.LLMClientFactory import LLMClientFactory
from core.llm_client.SystemPromptType import SystemPromptType

from core.utils.JsonResponseExtractorByRegex import JsonResponseExtractorByRegex

logger = logging.getLogger("ai_agent.core.controller")
logger.setLevel(logging.DEBUG)

class Controller:
    def __init__(self):

        self.llm_client = LLMClientFactory.get_llm_client()
        logger.info(f"\nLLM Client initialized: {self.llm_client}\n")

        # Регистрируем обработчики
        self.handlers: Dict[str, HandlerBase] = {
            "find_file_by_prefix": HandlerFindFileByPrefix(),
            "find_text_in_files": HandlerFindTextInFiles(),
        }

        # Инициализация экстрактора JSON через regex
        self.json_extractor_regex = JsonResponseExtractorByRegex(debug=True)


    async def prepareMacroPromptAndTalkToLLM(self, message: str) -> Dict[str, Any]:
        logger.info(f"[Controller] Получен запрос: {message}")

        # Просто отправляем сообщение вместе с типом системного промпта MACRO_TASK
        llm_response_text = await self.llm_client.send_message(
            message,
            prompt_type=SystemPromptType.MACRO_TASK
        )

        try:
            instructions = self.json_extractor_regex.extract(llm_response_text)
            logger.info(f"\n[{self.__class__.__name__}] Ответ очищен от мусора:\n{instructions}\n")
        except Exception as e:
            logger.error(f"[Controller] Ошибка разбора JSON: {e}\n")
            return {"error": f"Не удалось разобрать ответ LLM: {str(e)}\n"}

        # instructions = instructions.get("instructions", [])
        print(instructions)

        if not instructions:
            logger.error("\n[Controller] LLM не вернул никаких действий.\n")
            return {"\nerror": "LLM не вернул никаких действий.\n"}

        results = []
        for instruction in instructions:
            action_type = instruction.get("action", "DOES_NOT_EXIST")  # важно: тут должно быть "action", а не "type"

            if action_type == "DOES_NOT_EXIST":
                logger.info(f"[Controller] Обнаружено неподдерживаемая инструкция: {instruction.get("actions")}")
                results.append(instruction)

            logger.info(f"[Controller] Обрабатываю действие: {action_type}")

            # handler = next((h for h in self.handlers if h.can_handle(action_type)), None)
            handler = self.handlers.get(action_type)

            if handler:
                result = await handler.handle(instruction)
                results.append(result)
            else:
                logger.warning(f"[Controller] Неподдерживаемый тип действия: {action_type}")
                results.append({
                    "action": instruction,
                    "result": {"error": f"Неподдерживаемый тип действия: {action_type}"}
                })

        return {"results": results}