# core/llm_client/LLMClientFactory.py

import logging
from settings.Config import Config
from core.llm_client.LLMClientBase import LLMClientBase
from core.llm_client.LLMClientOpenRouter import LLMClientOpenRouter
from core.llm_client.LLMClientFake import LLMClientBaseFake
from core.llm_client.LLMClientMock import LLMClientMock
from core.llm_client.LLMClientGemini import LLMClientGemini

logger = logging.getLogger("ai_agent.core.llm_client.factory")

class LLMClientFactory:

    @staticmethod
    def get_llm_client() -> LLMClientBase:
        logger.info(f"[LLMClientFactory] Выбор LLM провайдера: {Config.LLM_PROVIDER}")
        if Config.LLM_PROVIDER.lower() == "gigachat":
            return LLMClientBaseFake()

        elif Config.LLM_PROVIDER == "gemini":
            return LLMClientGemini()

        elif Config.LLM_PROVIDER.lower() == "openrouter":
            return LLMClientOpenRouter()

        elif Config.LLM_PROVIDER.lower() == "mockllm":
            return LLMClientMock(debug=True)
