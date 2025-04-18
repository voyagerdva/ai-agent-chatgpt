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

@router.post("/find_file_in_folder")
async def findFileInFolderCommand(request: CommandRequest):
    logger.info(f"[Routes] Получен запрос: {request.message}")
    if not request.message:
        raise HTTPException(status_code=400, detail="Поле 'message' обязательно.")
    result = await agent.preparePromptAndTalkToLLM(request.message)
    logger.info(f"[Routes] Возвращаю результат: {result}")
    return result

@router.post("/find_text_in_files")
async def findTextInFilesCommand(request: CommandRequest):
    message = f"Найди все файлы, содержащие строку '{request.message}'"
    result = await agent.preparePromptAndTalkToLLM(message)
    return result
