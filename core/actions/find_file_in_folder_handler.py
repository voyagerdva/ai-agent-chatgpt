# core/actions/find_file_in_folder_handler.py

from typing import Dict, Any
from file_manager.file_manager import FileManager
from core.actions.ActionHandlerBase import ActionHandlerBase
from core.models.result import ActionResult


class FindFileInFolderHandlerBase(ActionHandlerBase):
    def __init__(self):
        self.file_manager = FileManager()

    def can_handle(self, action_type: str) -> bool:
        return action_type == "find_file_in_folder"

    async def handle(self, action: Dict[str, Any]) -> Dict[str, Any]:
        directory = action.get("directory")
        filename = action.get("filename")
        result: ActionResult = self.file_manager.find_file_in_folder(directory, filename)
        return {
            "action": {
                "type": "find_file_in_folder",
                "directory": directory,
                "filename": filename
            },
            "result": result.dict()
        }