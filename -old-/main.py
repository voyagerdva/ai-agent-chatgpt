import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import openai

# Загружаем переменные окружения из .env
load_dotenv()

# Устанавливаем ключ и кастомный endpoint OpenRouter
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.base_url = "https://openrouter.ai/api/v1"

# Проверка на наличие ключа
if not openai.api_key:
    raise RuntimeError("Переменная окружения OPENROUTER_API_KEY не установлена!")

# FastAPI приложение
app = FastAPI()

# Pydantic модель запроса
class MessageRequest(BaseModel):
    message: str

@app.post("/process")
async def process_message(request: MessageRequest):
    try:
        client = openai.AsyncOpenAI(
            api_key=openai.api_key,
            base_url=openai.base_url,
            default_headers={
                "HTTP-Referer": "http://localhost:8006",
                "X-Title": "Local FastAPI ChatBot"
            }
        )

        response = await client.chat.completions.create(
            model="deepseek/deepseek-r1-zero:free",  # можно заменить на другую модель
            messages=[
                {"role": "system", "content": "Ты — полезный русскоязычный ассистент."},
                {"role": "user", "content": request.message}
            ]
        )

        return {"response": response.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обращении к OpenRouter API: {str(e)}")

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8006, reload=True)
