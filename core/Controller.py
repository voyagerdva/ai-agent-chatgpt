# core/Controller.py

import logging
from typing import Dict, Any, List

from core.handlers.HandlerBase import HandlerBase
from core.handlers.HandlerFindFileByPrefix import HandlerFindFileByPrefix
from core.handlers.HandlerFindTextInFiles import HandlerFindTextInFiles
from core.handlers.HandlerCreateFiles import HandlerCreateFiles

from core.llm_client.LLMClientFactory import LLMClientFactory
from core.llm_client.SystemPromptType import SystemPromptType

from core.utils.JsonResponseExtractorByRegex import JsonResponseExtractorByRegex


import os
import importlib
import inspect
from core.handlers.HandlerBase import HandlerBase



logger = logging.getLogger("ai_agent.core.controller")
logger.setLevel(logging.DEBUG)

class Controller:
    def __init__(self):

        self.llm_client = LLMClientFactory.get_llm_client()
        logger.info(f"\nLLM Client initialized: {self.llm_client}\n")

        # Регистрируем обработчики
        # self.handlers: Dict[str, HandlerBase] = {
        #     "find_file_by_prefix": HandlerFindFileByPrefix(),
        #     "find_text_in_files": HandlerFindTextInFiles(),
        #     "create_files": HandlerCreateFiles(),
        # }
        self.handlers = {}
        self.scan_handlers()
        print("\n[Controller] Зарегистрированные хендлеры:")
        for action_type, handler in self.handlers.items():
            print(f"  • {action_type:25} → {handler.__class__.__name__}")

        # Инициализация экстрактора JSON через regex
        self.json_extractor_regex = JsonResponseExtractorByRegex(debug=True)


    def scan_handlers(self):
        handlers_dir = "core.handlers"
        handlers_path = os.path.join(os.path.dirname(__file__), "Handlers")

        for file in os.listdir(handlers_path):
            if not file.endswith(".py") or file == "HandlerBase.py":
                continue

            module_name = file[:-3]  # remove .py
            full_module_name = f"{handlers_dir}.{module_name}"

            module = importlib.import_module(full_module_name)

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, HandlerBase) and obj is not HandlerBase:
                    action_type = obj.get_action_type()
                    self.handlers[action_type] = obj()


    async def prepareMacroPromptAndTalkToLLM(self, message: str) -> Dict[str, Any]:
        logger.info(f"[Controller] Получен запрос: {message}")

        # Просто отправляем сообщение вместе с типом системного промпта MACRO_TASK
        llm_response_text = await self.llm_client.send_message(
            message,
            prompt_type=SystemPromptType.MACRO_TASK
        )

        logger.info(f"\n[LLM RAW RESPONSE]:\n{llm_response_text}\n")

        try:
            instructions = self.json_extractor_regex.extract(llm_response_text)
            logger.info(f"\n[{self.__class__.__name__}] Ответ очищен от мусора:\n{instructions}\n")
        except Exception as e:
            logger.error(f"[Controller] Ошибка разбора JSON: {e}\n")
            with open("llm_raw_output_debug.txt", "w", encoding="utf-8") as f:
                f.write(llm_response_text)
            return {"error": f"Не удалось разобрать ответ LLM: {str(e)}\n"}

        # instructions = instructions.get("instructions", [])
        print(instructions)

        if not instructions:
            logger.error("\n[Controller] LLM не вернул никаких действий.\n")
            return {"\nerror": "LLM не вернул никаких действий.\n"}

        results = []
        for instruction in instructions:
            action_type = instruction.get("action", "DOES_NOT_EXIST")

            if action_type == "DOES_NOT_EXIST":
                logger.info(f"[Controller] Обнаружено неподдерживаемая инструкция: {instruction.get("actions")}")
                results.append(instruction)

            logger.info(f"[Controller] Обрабатываю действие: {action_type}")

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