import re
import json
from typing import Any, Optional
from pydantic import BaseModel, ValidationError


class JsonResponseExtractorByRegexOLD:
    """
    Извлекает JSON из хаотичных текстов, возвращаемых LLM (с markdown, \boxed, мусором и т.д.)
    """

    def __init__(self, debug: bool = False):
        self.debug = debug

    def _log(self, message: str):
        if self.debug:
            print(f"[JsonResponseExtractor] {message}")

    def extract(self, raw_text: str) -> Any:
        """
        Главный метод: применяет серию стратегий для извлечения первого валидного JSON.
        """
        self._log("Старт извлечения JSON...")

        strategies = [
            self._extract_entire_cleaned_text,
            self._extract_with_raw_decode,
            self._extract_first_json_block,
        ]

        for strategy in strategies:
            try:
                result = strategy(raw_text)
                self._log(f"Успешно сработала стратегия: {strategy.__name__}")
                return result
            except Exception as e:
                self._log(f"Стратегия {strategy.__name__} провалилась: {e}")

        raise ValueError("Не удалось извлечь корректный JSON из текста.")

    def extract_validated(self, raw_text: str, model: type[BaseModel]) -> BaseModel:
        """
        Извлекает JSON и проверяет, что он соответствует Pydantic-модели.
        """
        raw_data = self.extract(raw_text)

        try:
            return model.parse_obj(raw_data)
        except ValidationError as e:
            self._log(f"Pydantic validation failed: {e}")
            raise

    def _extract_entire_cleaned_text(self, text: str) -> Any:
        """
        Пробует очистить текст и распарсить его целиком.
        """
        cleaned = self._clean_text(text)
        return json.loads(cleaned)

    def _extract_with_raw_decode(self, text: str) -> Any:
        """
        Использует json.JSONDecoder().raw_decode, чтобы найти JSON внутри текста.
        """
        decoder = json.JSONDecoder()
        cleaned = self._clean_text(text)

        for i in range(len(cleaned)):
            try:
                obj, _ = decoder.raw_decode(cleaned[i:])
                return obj
            except json.JSONDecodeError:
                continue
        raise ValueError("raw_decode не нашёл JSON")

    def _extract_first_json_block(self, text: str) -> Any:
        """
        Ищет первую фигурную скобку {…} или массив […], и пробует распарсить.
        """
        matches = re.findall(r'({.*?})|(\[.*?\])', text, flags=re.DOTALL)

        for obj, arr in matches:
            candidate = obj or arr
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
        raise ValueError("Не найден валидный JSON-блок")

    def _clean_text(self, text: str) -> str:
        """
        Удаляет лишние конструкции вроде \boxed{...}, markdown и прочее.
        """
        text = re.sub(r'\\boxed\s*\{', '', text)
        text = re.sub(r'```json|```', '', text)
        text = re.sub(r'\\n', '\n', text)
        text = text.strip()

        # Удаляем закрывающую } у boxed, если забыли удалить
        if text.endswith('}'):
            open_count = text.count('{')
            close_count = text.count('}')
            if close_count > open_count:
                text = text.rstrip('}')
        return text
