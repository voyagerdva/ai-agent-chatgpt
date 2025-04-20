# file_manager/file_manager.py

import os
import logging

logger = logging.getLogger("ai_agent.file_manager.file_manager")
logger.setLevel(logging.DEBUG)

class FileManager:
    def __init__(self):
        pass

    def find_file_in_folder(self, directory: str, filename: str) -> dict:
        logger.info(f"[FileManager] Поиск файла '{filename}' в каталоге '{directory}'")
        if not os.path.isdir(directory):
            logger.error(f"[FileManager] Каталог '{directory}' не существует или недоступен.")
            return {"error": f"Каталог '{directory}' не существует или недоступен."}

        for root, _, files in os.walk(directory):
            if filename in files:
                full_path = os.path.join(root, filename)
                logger.info(f"[FileManager] Файл найден: {full_path}")
                return {"found": True, "path": full_path}
        logger.info(f"[FileManager] Файл '{filename}' не найден.")
        return {"found": False, "message": f"Файл '{filename}' не найден в каталоге '{directory}'."}


    def find_text_in_files(self, directory: str, text: str) -> dict:
        logger.info(f"[FileManager] Поиск текста '{text}' в файлах каталога '{directory}'")

        if not os.path.isdir(directory):
            logger.error(f"[FileManager] Каталог '{directory}' не существует или недоступен.")
            return {"error": f"Каталог '{directory}' не существует или недоступен."}

        found_files = []

        for root, _, files in os.walk(directory):
            for file in files:
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if text in content:
                            found_files.append(full_path)
                except Exception as e:
                    logger.warning(f"[FileManager] Не удалось прочитать файл '{full_path}': {e}")

        return {"found_files": found_files}
