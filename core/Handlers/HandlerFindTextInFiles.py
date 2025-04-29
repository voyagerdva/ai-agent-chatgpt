# core/Handlers/HandlerFindTextInFiles.py

from typing import Dict, Any
from file_manager.FileManager import FileManager
from core.Handlers.HandlerBase import HandlerBase
from core.models.ActionResult import ActionResult


class HandlerFindTextInFiles(HandlerBase):
    def __init__(self):
        self.file_manager = FileManager()

    def can_handle(self, action_type: str) -> bool:
        return action_type == "find_text_in_files"

    async def handle(self, action: Dict[str, Any]) -> Dict[str, Any]:
        print(action)

        dir_path = action.get("params").get("directory")
        find_text = action.get("params").get("text")
        print(f"\ndir_path = {dir_path}")
        print(f"\nfind_text = {find_text}")

        result: ActionResult = self.file_manager.findTextInFiles(dir_path, find_text)

        return {
            "action": {
                "type": "find_text_in_files",
                "dir_path": dir_path,
                "find_text": find_text
            },
            "result": result.dict()
        }