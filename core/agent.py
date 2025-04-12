# core/agent.py

import logging
from typing import Dict, Any, List
from core.llm_client import get_llm_client
from file_manager.file_manager import FileManager

import json
import re

logger = logging.getLogger("ai_agent.core.agent")
logger.setLevel(logging.DEBUG)

class Agent:
    def __init__(self):
        self.llm_client = get_llm_client()  # выбираем LLM согласно настройкам
        self.file_manager = FileManager()

    def extract_json_from_response(self, response: str) -> dict:
        """
        Извлекает JSON-объект из строки, удаляя markdown-обертки и лишние символы.
        """
        try:
            # Удаляем markdown блоки и LaTeX конструкции, такие как \boxed и ```
            cleaned = re.sub(r"\\boxed", "", response)
            cleaned = re.sub(r"[`{}]+json", "", cleaned, flags=re.IGNORECASE)
            cleaned = cleaned.replace("```", "")
            cleaned = cleaned.replace("\\n", "\n")
            cleaned = cleaned.strip()

            # Находим первую и последнюю фигурную скобку
            # json_start = cleaned.find("{")
            # json_end = cleaned.rfind("}")
            # if json_start == -1 or json_end == -1:
            #     raise ValueError("Не удалось найти границы JSON-объекта")

            # json_str = cleaned[json_start:json_end + 1]
            # return json.loads(json_str)
            result = json.loads(cleaned)
            return result

        except Exception as e:
            raise ValueError(f"Ошибка при извлечении JSON из ответа LLM: {e}")


    async def process_message(self, message: str) -> Dict[str, Any]:
        logger.info(f"[Agent] Получен запрос: {message}")
        # Отправляем текст запроса в LLM и получаем ответ
        llm_response_text = await self.llm_client.send_message(message)

        # Пробуем разобрать JSON-ответ
        try:
            data = self.extract_json_from_response(llm_response_text)
        except Exception as e:
            logger.error(f"[Agent] Ошибка разбора JSON: {e}")
            return {"error": f"Не удалось разобрать ответ LLM: {str(e)}"}

        # Ожидаем, что LLM вернёт JSON вида:
        # { "actions": [{ "type": "find_file", "directory": "D:/tmp", "filename": "nano.txt" }] }
        actions: List[Dict[str, Any]] = data.get("actions", [])
        if not actions:
            logger.error("[Agent] LLM не вернул никаких действий.")
            return {"error": "LLM не вернул никаких действий."}

        results = []
        for action in actions:
            action_type = action.get("type")
            logger.info(f"[Agent] Обрабатываю действие: {action_type}")
            if action_type == "find_file":
                directory = action.get("directory")
                filename = action.get("filename")
                result = self.file_manager.find_file(directory, filename)
                logger.debug(f"[Agent] Результат поиска: {result}")
                results.append({"action": action, "result": result})
            else:
                logger.warning(f"[Agent] Неподдерживаемый тип действия: {action_type}")
                results.append({
                    "action": action,
                    "result": {"error": f"Неподдерживаемый тип действия: {action_type}"}
                })
        return {"results": results}
