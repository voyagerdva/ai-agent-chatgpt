# main.py

from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="ИИ-Агент для работы с файлами")

# Подключаем маршруты из пакета api
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8006, reload=True)
