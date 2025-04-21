import re
import json
from pydantic import BaseModel
from typing import Optional


class JsonResponseExtractorByRegex2methods:
    def __init__(self):
        """Инициализация класса JsonResponseExtractorByRegex."""
        pass

    def extractJson(self, rawText: str) -> Optional[str]:
        """Метод для извлечения JSON строки из текста с использованием регулярных выражений.

        Этот метод ищет потенциальный JSON в сыром тексте, обрабатывая его и очищая
        от всех лишних частей, таких как \boxed{} или markdown, чтобы оставить только чистый JSON.

        Args:
            rawText (str): Сырой текст с возможным JSON.

        Returns:
            Optional[str]: Очищенная строка JSON или None, если JSON не был найден.
        """
        # Убираем всё, что окружает JSON (например, \boxed{})
        json_str = re.sub(r"\\boxed{|\}", "", rawText)
        json_str = re.sub(r"```json|```", "", json_str)

        # Проверим, является ли это валидным JSON
        try:
            # Убираем лишние символы, если они есть
            json_str = json_str.strip()
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError:
            return None

    def extractValidated(self, rawText: str, model: type[BaseModel]) -> Optional[BaseModel]:
        """Метод для извлечения и валидации JSON с использованием модели Pydantic.

        Этот метод использует регулярные выражения для очистки сырого текста и
        извлекает JSON, после чего передает его на валидацию с помощью модели Pydantic.

        Args:
            rawText (str): Сырой текст с возможным JSON.
            model (type[BaseModel]): Модель Pydantic для валидации JSON.

        Returns:
            Optional[BaseModel]: Возвращает объект модели Pydantic, если данные валидны, иначе None.
        """
        # Извлекаем JSON
        json_str = self.extractJson(rawText)

        if json_str:
            # Преобразуем строку JSON в объект и проверяем на соответствие модели
            try:
                return model.parse_obj(json.loads(json_str))
            except Exception as e:
                print(f"Ошибка валидации: {e}")
                return None
        return None
