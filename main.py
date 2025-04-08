import os
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai

# Читаем API ключ из переменных окружения (его стоит задать в Windows, например, через PowerShell или .env файл)
openai.api_key = os.environ.get("OPENAI_API_KEY")

if not openai.api_key:
    raise Exception("Необходимо установить переменную окружения OPENAI_API_KEY.")


# Определяем модель данных для входящего запроса
class MessageRequest(BaseModel):
    message: str


# Создаём приложение FastAPI
app = FastAPI()


@app.post("/process")
async def process_message(request: MessageRequest):
    message = request.message
    if not message:
        raise HTTPException(status_code=400, detail="Поле 'message' должно быть заполнено.")

    # Составляем список сообщений для ChatGPT API, можно добавить системное сообщение для контекста
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": message}
    ]

    # Оборачиваем вызов API в asyncio.to_thread, чтобы не блокировать event loop
    try:
        response = await asyncio.to_thread(
            lambda: openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обращении к OpenAI API: {e}")

    # Извлекаем текст ответа
    try:
        answer_text = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise HTTPException(status_code=500, detail="Неверная структура ответа от API.")

    # Можно вернуть ответ в виде JSON
    return {"response": answer_text}


# Запуск через Uvicorn (можно запускать из командной строки)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8006)