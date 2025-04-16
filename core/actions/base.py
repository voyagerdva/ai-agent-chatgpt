# core/actions/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any


class ActionHandler(ABC):
    @abstractmethod
    def can_handle(self, action_type: str) -> bool:
        ...

    @abstractmethod
    async def handle(self, action: Dict[str, Any]) -> Dict[str, Any]:
        ...
