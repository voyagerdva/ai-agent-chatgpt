# tests/integration/test_api_endpoints.py

import os

def test_find_file_endpoint(client, tmp_path):
    # 1. Создаём подкаталог и файл
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    file_path = subdir / "hello.txt"
    file_path.write_text("контент")

    # 2. Формируем запрос
    message = f"найди файл hello.txt в каталоге {tmp_path}"
    payload = { "message": message }

    # 3. Делаем POST-запрос
    response = client.post("/find_file_in_folder", json=payload)

    # 4. Проверка
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["results"][0]["result"]["success"] is True
    assert json_data["results"][0]["result"]["data"] == str(file_path)
