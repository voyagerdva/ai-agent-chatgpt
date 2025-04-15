# main.py

from fastapi import FastAPI
from api.routes import router
import logging

# Настраиваем корневой логгер (если ещё не настроен)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="ИИ-Агент для работы с файлами")

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8008, access_log=True)