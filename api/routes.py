# api/routes.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from core.agent import Agent

router = APIRouter()
logger = logging.getLogger("ai_agent.api.routes")
logger.setLevel(logging.DEBUG)

class CommandRequest(BaseModel):
    message: str

# Инициализируем агента
agent = Agent()

@router.post("/process")
async def process_command(request: CommandRequest):
    logger.info(f"[Routes] Получен запрос: {request.message}")
    if not request.message:
        raise HTTPException(status_code=400, detail="Поле 'message' обязательно.")
    result = await agent.process_message(request.message)
    logger.info(f"[Routes] Возвращаю результат: {result}")
    return result
