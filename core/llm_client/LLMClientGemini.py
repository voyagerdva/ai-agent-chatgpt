# core/llm_client/LLMClientGemini.py
import google.generativeai as genai
from core.llm_client.LLMClientBase import LLMClientBase
from settings.Config import Config
import logging

logger = logging.getLogger("ai_agent.llm.gemini")


class LLMClientGemini(LLMClientBase):
    def __init__(self):
        super().__init__(model=Config.GEMINI_MODEL)
        self._configure_api()
        self.client = self._get_client()

    def _configure_api(self):
        """Конфигурация API без указания версии"""
        genai.configure(api_key=Config.GEMINI_API_KEY)

    def _get_client(self):
        return genai.GenerativeModel(self.model)

    def _get_completion(self, messages: list):
        system_prompt = next((m['content'] for m in messages if m['role'] == 'system'), "")
        user_prompt = next((m['content'] for m in messages if m['role'] == 'user'), "")

        response = self.client.generate_content(
            f"{system_prompt}\n\n{user_prompt}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.3
            )
        )
        return GeminiResponseAdapter(response)


# Обновляем адаптер
class GeminiResponseAdapter:
    def __init__(self, response):
        self.response = response

    @property
    def choices(self):
        return [ChoiceAdapter(self.response)]


class ChoiceAdapter:
    def __init__(self, response):
        self.response = response

    @property
    def message(self):
        return MessageAdapter(self.response)


class MessageAdapter:
    def __init__(self, response):
        self.response = response

    @property
    def content(self):
        if hasattr(self.response, 'text'):
            return self.response.text
        if hasattr(self.response, 'candidates') and self.response.candidates:
            return self.response.candidates[0].content.parts[0].text
        return "Ошибка: Неверный формат ответа Gemini"