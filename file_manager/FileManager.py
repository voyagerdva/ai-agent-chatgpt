# file_manager/FileManager.py

import os
import logging
from core.models.ActionResult import ActionResult


logger = logging.getLogger("ai_agent.file_manager.file_manager")
logger.setLevel(logging.DEBUG)


class FileManager:
    def __init__(self):
        pass

    def findFileinFolder(self, directory: str, filename: str) -> ActionResult:
        logger.info(f"[FileManager] Поиск файла '{filename}' в '{directory}'")
        if not os.path.isdir(directory):
            msg = f"Каталог '{directory}' не существует или недоступен."
            logger.error(f"[FileManager] {msg}")
            return ActionResult(success=False, message=msg)

        for root, _, files in os.walk(directory):
            if filename in files:
                full_path = os.path.join(root, filename)
                msg = f"Файл найден: {full_path}"
                logger.info(f"[FileManager] {msg}")
                return ActionResult(success=True, message=msg, data=full_path)

        msg = f"Файл '{filename}' не найден в '{directory}'."
        logger.info(f"[FileManager] {msg}")
        return ActionResult(success=False, message=msg)


    def find_text_in_files(self, directory: str, find_text: str) -> ActionResult:
        logger.info(f"[FileManager] Поиск текста '{find_text}' в '{directory}'")
        if not os.path.isdir(directory):
            msg = f"Каталог '{directory}' не существует или недоступен."
            logger.error(f"[FileManager] {msg}")
            return ActionResult(success=False, message=msg)

        found_files = []

        for root, _, files in os.walk(directory):
            for file in files:
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        if find_text in f.read():
                            found_files.append(full_path)
                except Exception as e:
                    logger.warning(f"[FileManager] Не удалось прочитать '{full_path}': {e}")

        if found_files:
            msg = f"Найдено файлов: {len(found_files)}"
            return ActionResult(success=True, message=msg, data=found_files)
        else:
            msg = f"Файлы с текстом '{find_text}' не найдены."
            return ActionResult(success=False, message=msg)
