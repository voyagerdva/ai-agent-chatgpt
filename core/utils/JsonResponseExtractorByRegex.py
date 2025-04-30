# core/utils/JsonResponseExtractorByRegex.py

import re
import json
from json import JSONDecoder, JSONDecodeError


class JsonResponseExtractorByRegex:
    """
    Извлекает первый валидный JSON-объект из произвольного текста,
    отбросив любую обёртку (\boxed{}, markdown, \n и т.п.).
    """

    def __init__(self, debug: bool = False):
        self.debug = debug

    def _log(self, msg: str):
        if self.debug:
            print(f"[JsonResponseExtractorByRegex] {msg}")

    import re

    @staticmethod
    def _fix_json_content(raw_json: str) -> str:
        """Автоматически экранирует переносы строк и кавычки в content"""
        pattern = re.compile(
            r'("content"\s*:\s*)"(.*?)"',
            flags=re.DOTALL | re.IGNORECASE
        )

        def _escape(match):
            content = match.group(2)
            content = content.replace('\\', '\\\\')  # Экранируем обратные слеши
            content = content.replace('\n', '\\n')  # Заменяем переносы
            content = content.replace('"', '\\"')  # Экранируем кавычки
            return f'{match.group(1)}"{content}"'

        return pattern.sub(_escape, raw_json)

    def extract(self, raw_text: str) -> dict:
        try:
            # 2. Очищаем от технического мусора
            cleaned = raw_text
            cleaned = re.sub(r'\\boxed', '', cleaned)  # убираем literal "\boxed"
            cleaned = re.sub(r'```json|```', '', cleaned)
            cleaned = cleaned.strip()

            # 1. Исправляем content-поля
            # fixed_text = self._fix_json_content(cleaned)

            # 3. Строгий парсинг JSON
            return json.loads(cleaned)

        except json.JSONDecodeError:
            # Fallback: Поиск JSON через raw_decode
            decoder = json.JSONDecoder()
            for i in range(len(cleaned)):
                try:
                    obj, _ = decoder.raw_decode(cleaned[i:])
                    return obj
                except json.JSONDecodeError:
                    continue
            raise ValueError("Invalid JSON")