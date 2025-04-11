# core/llm_client.py

import os
import openai
from settings.config import Config


class LLMClient:
    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.model = Config.LLM_MODEL  # Например: "deepseek/deepseek-r1-zero:free"
        openai.api_key = self.api_key
        openai.base_url = Config.OPENROUTER_API_BASE  # "https://openrouter.ai/api/v1"

    async def send_message(self, message: str) -> str:
        """
        Отправляет запрос в LLM и возвращает текст ответа.
        Ожидается, что LLM вернёт JSON-инструкцию для дальнейших действий.
        """
        try:
            response = await openai.chat.completions.acreate(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты эксперт по преобразованию команд на естественном языке в "
                            "JSON-инструкции. Если получишь команду вида: "
                            "\"найди на моем компьютере в каталоге d:/tmp файл с именем nano.txt\", "
                            "верни чистый JSON без пояснений, например:\n"
                            "{\"actions\": [{\"type\": \"find_file\", \"directory\": \"D:/tmp\", \"filename\": \"nano.txt\"}]}"
                        )
                    },
                    {"role": "user", "content": message}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f'{{"error": "Ошибка при вызове LLM: {str(e)}"}}'
