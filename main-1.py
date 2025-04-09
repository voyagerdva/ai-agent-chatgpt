import os
import subprocess
import asyncio
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import openai

# Загрузка переменных окружения из файла .env
load_dotenv()

# Настройка OpenRouter API: API-ключ и базовый URL
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.base_url = "https://openrouter.ai/api/v1"

if not openai.api_key:
    raise Exception("OPENROUTER_API_KEY не установлен в переменных окружения!")

# Создаём FastAPI приложение
app = FastAPI()

# Модель входящего запроса
class CommandRequest(BaseModel):
    message: str

# Модуль проверки допустимых действий (whitelist)
def validate_action(action: dict) -> bool:
    allowed_types = {"run_terminal"}
    return action.get("type") in allowed_types

# Модуль, выполняющий команду операционной системы
def execute_action(action: dict) -> dict:
    action_type = action.get("type")
    if action_type == "run_terminal":
        # Извлекаем параметры: тип терминала и каталог запуска
        terminal_type = action.get("terminal", "powershell")
        directory = action.get("directory", "D:/tmp")
        try:
            if terminal_type.lower() == "powershell":
                # Формируем команду для запуска PowerShell в указанном каталоге.
                # Флаг -NoExit оставляет окно открытым.
                command = f'powershell.exe -NoExit -Command "Set-Location \'{directory}\'"'
                subprocess.Popen(command, shell=True)
                return {"status": "ok", "message": f"PowerShell запущен в каталоге {directory}"}
            else:
                return {"status": "error", "error": "Поддерживаются только команды для PowerShell."}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return {"status": "error", "error": f"Неподдерживаемый тип действия: {action_type}"}

# Эндпойнт для обработки запроса
@app.post("/process")
async def process_message(request: CommandRequest):
    user_message = request.message
    if not user_message:
        raise HTTPException(status_code=400, detail="Поле 'message' должно быть заполнено.")

    # Отправляем запрос в LLM. В этом примере LLM должен вернуть JSON в формате:
    # {"actions": [{"type": "run_terminal", "terminal": "powershell", "directory": "D:/tmp"}]}
    try:
        response = await openai.chat.completions.acreate(
            model="deepseek/deepseek-r1-zero:free",  # выбираем модель, доступную через OpenRouter
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты являешься экспертом по конвертации команд на естественном языке в JSON-инструкции. "
                        "Если получишь команду типа 'открой на моем компьютере терминал powershell в каталоге d:/tmp', "
                        "верни ответ в виде следующего чистого JSON без пояснений:\n"
                        "{\"actions\": [{\"type\": \"run_terminal\", \"terminal\": \"powershell\", \"directory\": \"D:/tmp\"}]}"
                    )
                },
                {"role": "user", "content": user_message}
            ]
        )
        llm_text = response.choices[0].message.content
        # Пытаемся распарсить ответ как JSON
        actions_data = json.loads(llm_text)
        actions = actions_data.get("actions", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обращении к LLM: {e}")

    if not actions:
        raise HTTPException(status_code=500, detail="LLM не вернул действия.")

    results = []
    # Валидируем и выполняем каждое действие
    for action in actions:
        if validate_action(action):
            result = await asyncio.to_thread(execute_action, action)
            results.append({"action": action, "result": result})
        else:
            results.append({"action": action, "result": {"status": "error", "error": "Недопустимое действие"}})

    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8006, reload=True)
