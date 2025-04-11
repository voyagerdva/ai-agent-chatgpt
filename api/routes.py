# api/routes.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.agent import Agent
from core.llm_client import LLMClient
from file_manager.file_manager import FileManager

router = APIRouter()

class CommandRequest(BaseModel):
    message: str

# Инициализируем необходимые компоненты
llm_client = LLMClient()
file_manager = FileManager()
agent = Agent(llm_client, file_manager)

@router.post("/process")
async def process_command(request: CommandRequest):
    if not request.message:
        raise HTTPException(status_code=400, detail="Поле 'message' обязательно.")
    result = await agent.process_message(request.message)
    return result
