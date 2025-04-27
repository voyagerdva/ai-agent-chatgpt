# tests/unit/test_file_manager.py

import os
from file_manager.FileManager import FileManager

def test_find_file_in_folder(tmp_path):
    # 1. Создаём подкаталог
    subdir = tmp_path / "subdir"
    subdir.mkdir()

    # 2. Создаём файл
    file_path = subdir / "hello.txt"
    file_path.write_text("тестовый контент")

    # 3. Вызываем FileManager
    fm = FileManager()
    result = fm.findFileinFolder(str(tmp_path), "hello.txt")

    # 4. Проверяем результат
    assert result.success is True
    assert result.data == str(file_path)
