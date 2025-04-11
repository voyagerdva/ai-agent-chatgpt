''' Пример агента с доп. обработкой ответа от LLM - удаление лишних слешей, приведение в нормальный список'''
import os
import subprocess
import asyncio
import json
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import openai

# Загрузка переменных окружения
load_dotenv()

# Настройка OpenRouter API: ключ и базовый URL
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.base_url = "https://openrouter.ai/api/v1"

if not openai.api_key:
    raise Exception("OPENROUTER_API_KEY не установлен!")

app = FastAPI()


class CommandRequest(BaseModel):
    message: str


def extract_commands(llm_response: str) -> list:
    """
    Ищет блоки с тройными обратными кавычками (код-блоки),
    возможно, помеченные языком (например, powershell),
    и возвращает список строк внутри этих блоков.
    """
    # Исключаем обрамление "\box{" и "}"
    cleaned = llm_response.replace("\\box{", "").replace("}", "")
    pattern = r"```(?:powershell)?\s*(.*?)\s*```"
    commands = re.findall(pattern, cleaned, flags=re.DOTALL)
    return commands


def execute_powershell_command(command: str) -> dict:
    """
    Выполняет команду в PowerShell с использованием subprocess.Popen.
    """
    try:
        # Флаг -NoExit оставляет окно открытым после выполнения команды.
        full_command = f'powershell.exe -NoExit -Command "{command}"'
        subprocess.Popen(full_command, shell=True)
        return {"status": "ok", "message": f"Выполнена команда: {command}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# Простой whitelist: разрешаем только запуск терминала
def validate_action(action: dict) -> bool:
    allowed_types = {"run_terminal"}
    return action.get("type") in allowed_types


# Функция, которая принимает действие и выполняет его:
def execute_action(action: dict) -> dict:
    if action.get("type") == "run_terminal":
        # Здесь мы ожидаем, что LLM вернул блок или набор блоков с командами.
        llm_response = action.get("llm_response", "")
        commands = extract_commands(llm_response)
        if not commands:
            return {"status": "error", "error": "Не найдены команды в ответе"}
        # Для примера выбираем первую найденную команду
        command_to_run = commands[0]
        return execute_powershell_command(command_to_run)
    else:
        return {"status": "error", "error": "Неподдерживаемый тип действия"}


@app.post("/process")
async def process_message(request: CommandRequest):
    user_message = request.message
    if not user_message:
        raise HTTPException(status_code=400, detail="Поле 'message' должно быть заполнено.")

    # Отправляем запрос в LLM для получения структурированного ответа.
    # Наша система просит вернуть JSON со структурой { "actions": [ ... ] }.
    try:
        response = await openai.chat.completions.acreate(
            model="deepseek/deepseek-r1-zero:free",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты эксперт по интерпретации команд на естественном языке в JSON-инструкции. "
                        "Если получишь команду 'открой на моем компьютере терминал powershell в каталоге d:/tmp', "
                        "верни чистый JSON вида:\n"
                        "{\"actions\": [{\"type\": \"run_terminal\", \"llm_response\": \"<КОМАНДА>\"}]}\n"
                        "Где <КОМАНДА> — это код, обернутый в тройные обратные кавычки, например:\n"
                        "\\box{```powershell\nSet-Location -Path 'D:\\tmp'\n```}"
                    )
                },
                {"role": "user", "content": user_message}
            ]
        )
        llm_text = response.choices[0].message.content
        # Пытаемся разобрать JSON, который вернул LLM
        actions_data = json.loads(llm_text)
        actions = actions_data.get("actions", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обращении к LLM: {e}")

    if not actions:
        raise HTTPException(status_code=500, detail="LLM не вернул действия.")

    results = []
    for action in actions:
        if validate_action(action):
            result = await asyncio.to_thread(execute_action, action)
            results.append({"action": action, "result": result})
        else:
            results.append({"action": action, "result": {"status": "error", "error": "Действие не разрешено"}})

    return {"results": results}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8006, reload=True)
