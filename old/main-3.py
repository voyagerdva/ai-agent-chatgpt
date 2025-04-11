'''
Ниже приведён пример, как можно доработать исполнительную часть агента для обработки ответа LLM, который возвращает многострочный скрипт PowerShell с несколькими шагами. В этом примере мы:
Извлекаем содержимое блока кода из ответа LLM (удаляем обёртку "\boxed{...}" и блоки кода).
Обрабатываем полученный скрипт (если он многострочный, его можно выполнить как единое целое).
Для выполнения скрипта создаём временный файл и запускаем его с помощью PowerShell.
Обратите внимание, что для безопасности рекомендуется очень тщательно проверять входящие команды, ведь запуск кода, полученного от LLM, может представлять риск.
'''
import os
import subprocess
import asyncio
import json
import re
import tempfile
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import openai

# Загрузка переменных окружения из .env
load_dotenv()

# Настройка OpenRouter API: ключ и базовый URL
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.base_url = "https://openrouter.ai/api/v1"

if not openai.api_key:
    raise Exception("OPENROUTER_API_KEY не установлен!")

app = FastAPI()


# Модель входящего запроса
class CommandRequest(BaseModel):
    message: str


def extract_commands(llm_response: str) -> str:
    """
    Извлекает содержимое первого блока с тройными обратными кавычками,
    предварительно убирая обёртку типа "\boxed{...}".
    Возвращает строку со скриптом PowerShell.
    """
    # Убираем "\boxed{" и завершающую "}" если они есть
    cleaned = llm_response.strip()
    if cleaned.startswith("\\boxed{"):
        cleaned = cleaned[len("\\boxed{"):]
    if cleaned.endswith("}"):
        cleaned = cleaned[:-1]

    # Ищем содержимое между тройными обратными кавычками (может быть с указанием языка)
    pattern = r"```(?:powershell)?\s*(.*?)\s*```"
    match = re.search(pattern, cleaned, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def execute_powershell_script(script: str) -> dict:
    """
    Выполняет скрипт PowerShell:
      - Создаёт временный .ps1 файл,
      - Запускает его через powershell.exe с параметром -NoExit,
      - Возвращает статус выполнения.
    """
    try:
        # Создаём временный файл для скрипта
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ps1", delete=False, encoding="utf-8") as temp_script:
            temp_script.write(script)
            script_path = temp_script.name

        # Собираем команду для запуска PowerShell, чтобы окно осталось открытым (-NoExit)
        full_command = f'powershell.exe -NoExit -File "{script_path}"'
        subprocess.Popen(full_command, shell=True)
        return {"status": "ok", "message": f"Запущен скрипт из файла: {script_path}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# Валидация – здесь можно ограничить поддерживаемые действия; пока оставим простую проверку
def validate_action(action: dict) -> bool:
    allowed_types = {"run_terminal"}
    return action.get("type") in allowed_types


def process_action_data(action: dict) -> dict:
    """
    Обрабатывает данные действия и извлекает скрипт PowerShell из поля llm_response.
    """
    llm_response = action.get("llm_response", "")
    script = extract_commands(llm_response)
    if not script:
        return {"status": "error", "error": "Не удалось извлечь скрипт из ответа."}
    return execute_powershell_script(script)


@app.post("/process")
async def process_message(request: CommandRequest):
    user_message = request.message
    if not user_message:
        raise HTTPException(status_code=400, detail="Поле 'message' должно быть заполнено.")

    # Отправляем запрос в LLM для получения структурированного ответа.
    # Ожидается, что LLM вернёт JSON со структурой:
    # {"actions": [{"type": "run_terminal", "llm_response": "<скрипт в блоке кода>"}]}
    try:
        response = await openai.chat.completions.acreate(
            model="deepseek/deepseek-r1-zero:free",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты — эксперт по преобразованию команд на естественном языке в JSON-инструкции. "
                        "Если получишь команду типа 'открой на моем компьютере терминал powershell в каталоге d:/tmp', "
                        "верни ответ в виде чистого JSON без пояснений, например:\n"
                        "{\"actions\": [{\"type\": \"run_terminal\", \"llm_response\": \"\\\\boxed{```powershell\\n# Шаг 1: Перейти на диск D (если необходимо)\\nD:\\\\n\\n# Шаг 2: Проверить наличие каталога D:\\\\tmp и создать его, если он не существует\\nif (-not (Test-Path \\\"D:\\\\tmp\\\")) {\\n    New-Item -ItemType Directory -Path \\\"D:\\\\tmp\\\"\\n}\\n\\n# Шаг 3: Перейти в каталог D:\\\\tmp\\ncd D:\\\\tmp\\n\\n# Шаг 4: Проверить текущий каталог\\nGet-Location\\n```}\"}]}"
                    )
                },
                {"role": "user", "content": user_message}
            ]
        )
        llm_text = response.choices[0].message.content
        # Разбираем JSON, возвращённый LLM
        actions_data = json.loads(llm_text)
        actions = actions_data.get("actions", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обращении к LLM: {e}")

    if not actions:
        raise HTTPException(status_code=500, detail="LLM не вернул действия.")

    results = []
    for action in actions:
        if validate_action(action):
            result = await asyncio.to_thread(process_action_data, action)
            results.append({"action": action, "result": result})
        else:
            results.append({"action": action, "result": {"status": "error", "error": "Действие не разрешено"}})

    return {"results": results}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8006, reload=True)
