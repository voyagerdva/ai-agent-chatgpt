# core/actions/HandlerFindTextInFiles.py

from typing import Dict, Any
from file_manager.FileManager import FileManager
from core.actions.HandlerBase import HandlerBase
from core.models.ActionResult import ActionResult


class HandlerFindTextInFiles(HandlerBase):
    def __init__(self):
        self.file_manager = FileManager()

    def can_handle(self, action_type: str) -> bool:
        return action_type == "find_text_in_files"

    async def handle(self, action: Dict[str, Any]) -> Dict[str, Any]:
        directory = action.get("directory")
        find_text = action.get("find_text")  # используем название как в JSON от LLM
        result: ActionResult = self.file_manager.find_text_in_files(directory, find_text)
        return {
            "action": {
                "type": "find_text_in_files",
                "directory": directory,
                "find_text": find_text
            },
            "result": result.dict()
        }