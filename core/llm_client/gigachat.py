# core/llm_client/gigachat.py

import asyncio
import logging
from openai import OpenAI
from core.llm_client.base import BaseLLMClient
from settings.config import Config

logger = logging.getLogger("ai_agent.core.llm_client.gigachat")


class GigaChatLLMClient(BaseLLMClient):
    def __init__(self):
        self.api_key = Config.GIGACHAT_API_KEY
        self.model = Config.GIGACHAT_MODEL
        self.client = OpenAI(api_key=self.api_key, base_url=Config.GIGACHAT_API_BASE)

    async def send_message(self, message: str) -> str:
        logger.info("[GigaChatLLMClient] Отправка запроса в LLM...")
        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Ты — эксперт по преобразованию команд на естественном языке в JSON-инструкции. "
                        "Если получишь команду вида: \"найди на моем компьютере в каталоге d:/tmp файл с именем nano.txt\", "
                        "верни чистый JSON без пояснений, например:\n"
                        "{\"actions\": [{\"type\": \"find_file\", \"directory\": \"D:/tmp\", \"filename\": \"nano.txt\"}]}"
                    )
                },
                {"role": "user", "content": message}
            ]

            response = await asyncio.to_thread(
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    timeout=30
                )
            )
            llm_text = response.choices[0].message.content
            logger.info(f"[GigaChatLLMClient] Получен ответ: {llm_text}")
            return llm_text

        except Exception as e:
            logger.error(f"[GigaChatLLMClient] Ошибка запроса: {e}")
            return f'{{"error": "Ошибка при вызове LLM: {str(e)}"}}'
