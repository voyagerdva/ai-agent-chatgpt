# core/Handlers/HandlerFindFileInFolder.py

from typing import Dict, Any
from file_manager.FileManager import FileManager
from core.Handlers.HandlerBase import HandlerBase
from core.models.ActionResult import ActionResult


class HandlerFindFileInFolder(HandlerBase):
    def __init__(self):
        self.file_manager = FileManager()

    def can_handle(self, action_type: str) -> bool:
        return action_type == "find_file_in_folder"

    async def handle(self, action: Dict[str, Any]) -> Dict[str, Any]:
        directory = action.get("directory")
        filename = action.get("filename")
        result: ActionResult = self.file_manager.findFileinFolder(directory, filename)
        return {
            "action": {
                "type": "find_file_in_folder",
                "directory": directory,
                "filename": filename
            },
            "result": result.dict()
        }