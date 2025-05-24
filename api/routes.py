#=== api/routes.py ================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from core.Controller import Controller

router = APIRouter()
logger = logging.getLogger("ai_agent.api.routes")
logger.setLevel(logging.DEBUG)

class CommandRequest(BaseModel):
    message: str

# Инициализируем агента
controller = Controller()


@router.post("/execute")
async def execute(request: CommandRequest):
    logger.info(f"[Routes] Получен запрос: {request.message}")
    if not request.message:
        raise HTTPException(status_code=400, detail="Поле 'message' обязательно.")

    result = await controller.prepareMacroPromptAndTalkToLLM(request.message)

    logger.info(
        f"[Routes] Сессия завершена (session_id={result.get('session_id')}, turns={result.get('turns')}, llm_calls={result.get('llm_calls')})"
    )
    return result
