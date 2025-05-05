# core/handlers/LLMClientBase.py
from abc import ABC, abstractmethod
from typing import Dict, Any


class HandlerBase(ABC):

    @abstractmethod
    async def handle(self, action: Dict[str, Any]) -> Dict[str, Any]:
        ...

    def can_handle(self, action_type: str) -> bool:
        return action_type == self.get_action_type()

    def get_action_type(self):
        pass