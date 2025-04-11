# core/agent.py

import json
import logging
from typing import Dict, Any, List
from core.llm_client import get_llm_client
from file_manager.file_manager import FileManager

logger = logging.getLogger("ai_agent.core.agent")
logger.setLevel(logging.DEBUG)

class Agent:
    def __init__(self):
        self.llm_client = get_llm_client()  # выбираем LLM согласно настройкам
        self.file_manager = FileManager()

    async def process_message(self, message: str) -> Dict[str, Any]:
        logger.info(f"[Agent] Получен запрос: {message}")
        # Отправляем текст запроса в LLM и получаем ответ
        llm_response_text = await self.llm_client.send_message(message)
        logger.debug(f"[Agent] Ответ LLM: {llm_response_text}")

        # Пробуем разобрать JSON-ответ
        try:
            data = json.loads(llm_response_text)
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
