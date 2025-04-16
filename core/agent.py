# core/agent.py

import logging
import json
import re
from typing import Dict, Any, List

from core.actions.base import ActionHandler
from core.actions.find_file_in_folder_handler import FindFileInFolderHandler
from core.actions.find_text_handler import FindTextInFilesHandler

from core.llm_client.factory import get_llm_client
from core.llm_client.prompts import PromptType
# from core.llm_client.gigachat import GigaChatLLMClient

logger = logging.getLogger("ai_agent.core.agent")
logger.setLevel(logging.DEBUG)


class Agent:
    def __init__(self):
        self.llm_client = get_llm_client()
        # Регистрируем все обработчики здесь:
        self.handlers: List[ActionHandler] = [
            FindFileInFolderHandler(),
            FindTextInFilesHandler(),
        ]

    def get_prompt_for_message(self, message: str) -> PromptType:
        msg_lower = message.lower()
        if "файл" in msg_lower or "найди файл" in msg_lower:
            return PromptType.FIND_FILE_IN_FOLDER
        elif "строку" in msg_lower or "найди строку" in msg_lower:
            return PromptType.FIND_TEXT
        else:
            return PromptType.GENERIC


    def extract_json_from_response(self, response: str) -> dict:
        try:
            cleaned = re.sub(r"\\boxed", "", response)
            cleaned = re.sub(r"[`{}]+json", "", cleaned, flags=re.IGNORECASE)
            cleaned = cleaned.replace("```", "")
            cleaned = cleaned.replace("\\n", "\n")
            cleaned = cleaned.strip()
            return json.loads(cleaned)
        except Exception as e:
            raise ValueError(f"Ошибка при извлечении JSON из ответа LLM: {e}")

    async def preparePromptAndTalkToLLM(self, message: str) -> Dict[str, Any]:
        logger.info(f"[Agent] Получен запрос: {message}")

        prompt_type = self.get_prompt_for_message(message)
        llm_response_text = await self.llm_client.send_message(message, prompt_type=prompt_type)

        try:
            data = self.extract_json_from_response(llm_response_text)
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

