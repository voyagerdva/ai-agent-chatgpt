# core/agent.py

import logging
import json
import re
from typing import Dict, Any, List

from core.actions.ActionHandlerBase import ActionHandlerBase
from core.actions.find_file_in_folder_handler import FindFileInFolderHandlerBase
from core.actions.find_text_in_files_handler import FindTextInFilesHandlerBase

from core.llm_client.factory import get_llm_client
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
        self.llm_client = get_llm_client()
        print(f"\n{self.llm_client}\n")

        # Регистрируем все обработчики здесь:
        self.handlers: List[ActionHandlerBase] = [
            FindFileInFolderHandlerBase(),
            FindTextInFilesHandlerBase(),
        ]

        # Инициализация экстрактора для регулярных выражений
        # self.json_extractor_regex = JsonResponseExtractorByRegex()
        self.json_extractor_regex = JsonResponseExtractorByRegex(debug=True)
        # self.json_extractor_regex = JsonResponseExtractorByModelFilter()


    async def preparePromptAndTalkToLLM(self, prompt: str) -> dict:
        raw_response = await self.llm_client.ask(prompt)
        return self.json_extractor.extract(raw_response)



    async def preparePromptAndTalkToLLM(self, message: str) -> Dict[str, Any]:
        logger.info(f"[Agent] Получен запрос: {message}")

        prompt_type = self.get_prompt_for_message(message)
        llm_response_text = await self.llm_client.send_message(message, prompt_type=prompt_type)

        # Используем экземпляр экстрактора
        try:
            # data = self.extract_json_from_response(llm_response_text)
            # data = self.json_extractor_regex.extract(llm_response_text, ActionResult)
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


