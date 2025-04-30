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

    def extract(self, rawText: str) -> dict:
        """
        1) Очищаем от markdown/boxed/etc
        2) Ищем первый валидный JSON-объект с помощью raw_decode
        """
        # 1) предварительная грубая чистка обёрток
        cleaned = rawText
        cleaned = re.sub(r'\\boxed', '', cleaned)               # убираем literal "\boxed"
        cleaned = re.sub(r'```json|```', '', cleaned)           # убираем markdown fences
        cleaned = cleaned.replace(r'\n', '\n')                  # реальные переводы строки
        cleaned = cleaned.strip()

        if self.debug:
            self._log(f"Cleaned text:\n{cleaned}\n-----")

        # 2) попробуем найти JSON где-нибудь внутри
        decoder = JSONDecoder()
        idx = 0
        text_len = len(cleaned)
        while idx < text_len:
            try:
                obj, offset = decoder.raw_decode(cleaned[idx:])
                if self.debug:
                    self._log(f"Decoded JSON at pos {idx}, length {offset}")
                return obj
            except JSONDecodeError as e:
                self._log(f"JSONDecodeError at pos {idx}: {e}")
                idx += 1

        raise ValueError("JSON‑блок не найден в ответе LLM")
