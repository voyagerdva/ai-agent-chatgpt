# core/handlers/HandlerCreateFiles.py

from typing import Dict, Any
from file_manager.FileManager import FileManager
from core.handlers.HandlerBase import HandlerBase
from core.models.ActionResult import ActionResult


class HandlerCreateFiles(HandlerBase):
    def __init__(self):
        self.file_manager = FileManager()


    @staticmethod
    def get_action_type() -> str:
        return "create_files"

    async def handle(self, action: Dict[str, Any]) -> Dict[str, Any]:
        files_data = action.get("params", {}).get("files", [])

        result: ActionResult = self.file_manager.createFiles(files_data)

        return {
            "action": {
                "type": self.get_action_type(),
                "files": files_data
            },
            "result": result.dict()
        }
