# core/Handlers/HandlerFindFileInFolder.py

from typing import Dict, Any
from file_manager.FileManager import FileManager
from core.Handlers.HandlerBase import HandlerBase
from core.models.ActionResult import ActionResult


class HandlerFindFileByPrefix(HandlerBase):
    def __init__(self):
        self.file_manager = FileManager()

    def can_handle(self, action_type: str) -> bool:
        return action_type == "find_file_by_prefix"

    async def handle(self, action: Dict[str, Any]) -> Dict[str, Any]:
        dir_path = action.get("params").get("directory")
        prefix = action.get("params").get("prefix")
        result: ActionResult = self.file_manager.findFileByPrefix(dir_path, prefix)
        return {
            "action": {
                "type": "find_file_by_prefix",
                "directory": dir_path,
                "prefix": prefix
            },
            "result": result.dict()
        }