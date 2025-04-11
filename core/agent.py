# core/agent.py

from typing import Dict, Any, List
from core.llm_client import LLMClient
from file_manager.file_manager import FileManager
import json

class Agent:
    def __init__(self, llm_client: LLMClient, file_manager: FileManager):
        self.llm_client = llm_client
        self.file_manager = file_manager

    async def process_message(self, message: str) -> Dict[str, Any]:
        """
        Принимает текст запроса, отправляет его в LLM,
        получает JSON с инструкциями и выполняет их.
        """
        # Получаем инструкцию от LLM
        llm_response_text = await self.llm_client.send_message(message)
        try:
            data = json.loads(llm_response_text)
        except Exception as e:
            # Если не получается разобрать как JSON – возвращаем ошибку.
            return {"error": f"Не удалось разобрать ответ LLM: {str(e)}"}

        # Ожидаем, что LLM вернул JSON вида:
        # { "actions": [{"type": "find_file", "directory": "D:/tmp", "filename": "nano.txt" }] }
        actions: List[Dict[str, Any]] = data.get("actions", [])
        if not actions:
            return {"error": "LLM не вернул никаких действий."}

        results = []
        for action in actions:
            action_type = action.get("type")
            if action_type == "find_file":
                directory = action.get("directory")
                filename = action.get("filename")
                result = self.file_manager.find_file(directory, filename)
                results.append({"action": action, "result": result})
            else:
                results.append({
                    "action": action,
                    "result": {"error": f"Неподдерживаемый тип действия: {action_type}"}
                })
        return {"results": results}
