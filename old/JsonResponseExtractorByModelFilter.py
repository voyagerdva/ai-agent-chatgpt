# core\utils\JsonResponseExtractorByModelFilter.py

import json
from pydantic import BaseModel
from typing import Optional


class JsonResponseExtractorByModelFilter:
    def __init__(self):
        """Инициализация класса JsonResponseExtractorByModelFilter."""
        pass

    def extract(self, raw_text: str, model: type[BaseModel]) -> Optional[BaseModel]:
        """Извлекает и фильтрует данные через модель Pydantic.

        Этот метод пытается преобразовать строку в JSON и фильтрует её через модель Pydantic.

        Args:
            raw_text (str): Сырой текст с возможным JSON.
            model (type[BaseModel]): Модель Pydantic для фильтрации и валидации.

        Returns:
            Optional[BaseModel]: Возвращает объект модели Pydantic, если данные соответствуют модели, иначе None.
        """
        try:
            json_data = json.loads(raw_text)
        except json.JSONDecodeError:
            return None

        # Фильтруем и валидируем через модель
        try:
            return model.parse_obj(json_data)
        except Exception as e:
            print(f"Ошибка валидации: {e}")
            return None
