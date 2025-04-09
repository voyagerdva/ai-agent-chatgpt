'''
Ниже приведён обновлённый вариант кода, который обрабатывает ситуацию, когда LLM возвращает либо JSON‑структуру с ключом "actions", либо простой текст в поле "response". В случае неудачи парсинга мы формируем одно действие с типом "run_terminal" и значением llm_response, после чего извлекаем команду из этого текста и выполняем её.

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
    предварительно убирая возможную обёртку типа "\boxed{...}".
    Возвращает строку со скриптом PowerShell.
    """
    cleaned = llm_response.strip()
    if cleaned.startswith("\\boxed{"):
        cleaned = cleaned[len("\\boxed{"):]
    if cleaned.endswith("}"):
        cleaned = cleaned[:-1]

    # Ищем содержимое между тройными обратными кавычками с необязательным языком (например, powershell)
    pattern = r"```(?:powershell)?\s*(.*?)\s*```"
    match = re.search(pattern, cleaned, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def execute_powershell_script(script: str) -> dict:
    """
    Записывает скрипт PowerShell во временный файл и запускает его через powershell.exe с флагом -NoExit.
    """
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ps1", delete=False, encoding="utf-8") as temp_script:
            temp_script.write(script)
            script_path = temp_script.name

        full_command = f'powershell.exe -NoExit -File "{script_path}"'
        subprocess.Popen(full_command, shell=True)
        return {"status": "ok", "message": f"Скрипт запущен: {script_path}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# Функция валидации – на данном этапе разрешено только действие run_terminal
def validate_action(action: dict) -> bool:
    allowed_types = {"run_terminal"}
    return action.get("type") in allowed_types


def process_action_data(action: dict) -> dict:
    """
    Извлекает скрипт из поля 'llm_response' и запускает его.
    """
    llm_response = action.get("llm_response", "")
    script = extract_commands(llm_response)
    if not script:
        return {"status": "error", "error": "Не удалось извлечь скрипт из LLM-ответа."}
    return execute_powershell_script(script)


@app.post("/process")
async def process_message(request: CommandRequest):
    user_message = request.message
    if not user_message:
        raise HTTPException(status_code=400, detail="Поле 'message' должно быть заполнено.")

    # Отправляем запрос в LLM, ожидая получить JSON с инструкциями.
    try:
        response = await openai.chat.completions.acreate(
            model="deepseek/deepseek-r1-zero:free",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты — эксперт по преобразованию команд на естественном языке в JSON-инструкции. "
                        "Если получишь команду 'открой на моем компьютере терминал powershell в каталоге d:/tmp', "
                        "верни ответ в виде чистого JSON без пояснений. "
                        "Пример ответа:\n"
                        "{\"actions\": [{\"type\": \"run_terminal\", \"llm_response\": \"\\\\boxed{```powershell\\ncd D:\\\\tmp\\n```}\"}]}"
                    )
                },
                {"role": "user", "content": user_message}
            ]
        )
        llm_text = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обращении к LLM: {e}")

    # Пытаемся разобрать LLM-ответ как JSON
    actions = []
    try:
        data = json.loads(llm_text)
        if "actions" in data:
            actions = data["actions"]
        elif "response" in data:
            actions = [{"type": "run_terminal", "llm_response": data["response"]}]
    except Exception as e:
        # Если не удалось распарсить как JSON, то считаем весь текст ответом
        actions = [{"type": "run_terminal", "llm_response": llm_text}]

    if not actions:
        raise HTTPException(status_code=500, detail="LLM не вернул инструкции.")

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
