# file_manager/file_manager.py

import os


class FileManager:
    def __init__(self):
        pass

    def find_file(self, directory: str, filename: str) -> dict:
        """
        Ищет файл с именем filename в каталоге directory.
        Возвращает словарь с результатом: найден или нет, и путь к файлу.
        """
        if not os.path.isdir(directory):
            return {"error": f"Каталог '{directory}' не существует или недоступен."}

        for root, _, files in os.walk(directory):
            if filename in files:
                full_path = os.path.join(root, filename)
                return {"found": True, "path": full_path}
        return {"found": False, "message": f"Файл '{filename}' не найден в каталоге '{directory}'."}
