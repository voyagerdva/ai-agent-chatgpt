# core/actions/find_file_handler.py
from typing import Dict, Any
from core.actions.base import ActionHandler
from file_manager.file_manager import FileManager


class FindFileHandler(ActionHandler):
    def __init__(self):
        self.file_manager = FileManager()

    def can_handle(self, action_type: str) -> bool:
        return action_type == "find_file"

    async def handle(self, action: Dict[str, Any]) -> Dict[str, Any]:
        directory = action.get("directory")
        filename = action.get("filename")
        result = self.file_manager.find_file(directory, filename)
        return {"action": action, "result": result}
