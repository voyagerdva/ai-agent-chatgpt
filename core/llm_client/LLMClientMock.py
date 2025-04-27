# core/llm_client/LLMClientMock.py

import random
from core.llm_client.LLMClientBase import LLMClientBase
from mock_data.fake_llm_responses import find_file_in_folder_responses, find_text_in_files_responses
from core.llm_client.PromptType import PromptType

class LLMClientMock(LLMClientBase):
    def __init__(self, debug: bool = False):
        super().__init__(model="mock")
        self.debug = debug

    async def send_message(self, message: str, prompt_type: PromptType = PromptType.GENERIC) -> str:
        # Выбираем нужный пул ответов по типу prompt
        if prompt_type == PromptType.FIND_FILE_IN_FOLDER:
            pool = find_file_in_folder_responses
        elif prompt_type == PromptType.FIND_TEXT_IN_FILES:
            pool = find_text_in_files_responses
        else:
            # на всякий случай общее
            pool = find_file_in_folder_responses + find_text_in_files_responses

        reply = random.choice(pool)
        if self.debug:
            print(f"[MockLLMClient] Selected fake reply for {prompt_type}:\n{reply}\n")
        return reply

    def _get_client(self):
        return None
    def _get_completion(self, messages: list):
        return None
