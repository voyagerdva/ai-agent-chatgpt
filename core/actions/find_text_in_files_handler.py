# core/actions/find_text_in_files_handler.py

from typing import Dict, Any
from core.actions.base import ActionHandler
from file_manager.file_manager import FileManager


class FindTextInFilesHandler(ActionHandler):
    def __init__(self):
        self.file_manager = FileManager()

    def can_handle(self, action_type: str) -> bool:
        return action_type == "find_text_in_files"

    async def handle(self, action: Dict[str, Any]) -> Dict[str, Any]:
        directory = action.get("directory")
        text = action.get("text")
        result = self.file_manager.find_text_in_files(directory, text)
        return {"action": action, "result": result}
