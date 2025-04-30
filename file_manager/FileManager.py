# file_manager/FileManager.py

import os
import logging
from sys import prefix
from turtledemo.sorting_animate import instructions1

from click import command

from core.models.ActionResult import ActionResult


logger = logging.getLogger("ai_agent.file_manager.file_manager")
logger.setLevel(logging.DEBUG)


class FileManager:
    def __init__(self):
        pass

    def findTextInFiles(self, directory: str, find_text: str) -> ActionResult:
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


    def findFileByPrefix(self, directory: str, prefix: str) -> ActionResult:
        logger.info(f"[FileManager] Поиск файла по префиксу в имени '{prefix}' в '{directory}'")

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
                        if file.startswith(prefix):
                            msg = f"Файл найден: {full_path}"
                            logger.info(f"[FileManager] {msg}")
                            found_files.append(full_path)
                except Exception as e:
                    logger.warning(f"[FileManager] Не удалось прочитать '{full_path}': {e}")

        if found_files:
            msg = f"Найдено файлов: {len(found_files)}"
            return ActionResult(success=True, message=msg, data=found_files )
        else:
            msg = f"Файлы с префиксом в имени '{prefix}' не найдены."
            return ActionResult(success=False, message=msg)


    def findFileByName(self, directory: str, prefix: str) -> ActionResult:
        logger.info(f"[FileManager] Поиск файла '{prefix}' в '{directory}'")
        if not os.path.isdir(directory):
            msg = f"Каталог '{directory}' не существует или недоступен."
            logger.error(f"[FileManager] {msg}")

            return ActionResult(success=False, message=msg)

        for root, _, files in os.walk(directory):
            if prefix in files:
                full_path = os.path.join(root, prefix)
                msg = f"Файл найден: {full_path}"
                logger.info(f"[FileManager] {msg}")
                return ActionResult(success=True, message=msg, data=full_path)

        msg = f"Файл '{prefix}' не найден в '{directory}'."
        logger.info(f"[FileManager] {msg}")
        return ActionResult(success=False, message=msg)


    def createFiles(self, files_data: list[dict]) -> ActionResult:
        """
        Создание нескольких файлов с заданным контентом.

        :param files_data: список словарей с полями:
            - path: полный путь до файла (включая имя и расширение)
            - content: содержимое, которое нужно записать в файл
        :return: ActionResult с результатом выполнения
        """
        logger.info(f"[FileManager] Запуск создания {len(files_data)} файлов")

        created_files = []
        skipped_files = []
        errors = []

        for i, file_info in enumerate(files_data):
            path = file_info.get("path")
            content = file_info.get("content")

            if not path or not isinstance(content, str):
                error_msg = f"[FileManager] Неверные данные на итерации {i}: path='{path}', content='{content}'"
                logger.error(error_msg)
                errors.append(error_msg)
                continue

            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)

                if os.path.exists(path):
                    logger.warning(f"[FileManager] Файл уже существует, пропущен: {path}")
                    skipped_files.append(path)
                    continue

                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)

                logger.info(f"[FileManager] Файл создан: {path}")
                created_files.append(path)

            except Exception as e:
                error_msg = f"[FileManager] Ошибка при создании файла '{path}': {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        message_parts = []
        if created_files:
            message_parts.append(f"Создано файлов: {len(created_files)}.")
        if skipped_files:
            message_parts.append(f"Пропущено (уже существуют): {len(skipped_files)}.")
        if errors:
            message_parts.append(f"Ошибки: {len(errors)}.")

        return ActionResult(
            success=len(errors) == 0,
            message=" ".join(message_parts),
            data={
                "created": created_files,
                "skipped": skipped_files,
                "errors": errors
            }
        )
        