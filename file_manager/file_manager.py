# file_manager/file_manager.py

import os
import logging

logger = logging.getLogger("ai_agent.file_manager.file_manager")
logger.setLevel(logging.DEBUG)

class FileManager:
    def __init__(self):
        pass

    def find_file(self, directory: str, filename: str) -> dict:
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
