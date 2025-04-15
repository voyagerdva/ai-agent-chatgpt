# core/llm_client/base.py

import abc

class BaseLLMClient(abc.ABC):
    @abc.abstractmethod
    async def send_message(self, message: str) -> str:
        pass
