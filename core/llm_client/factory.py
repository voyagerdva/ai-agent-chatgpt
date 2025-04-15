# core/llm_client/factory.py

import logging
from settings.config import Config
from core.llm_client.base import BaseLLMClient
from core.llm_client.openrouter import OpenRouterLLMClient
from core.llm_client.gigachat import GigaChatLLMClient

logger = logging.getLogger("ai_agent.core.llm_client.factory")


def get_llm_client() -> BaseLLMClient:
    logger.info(f"[LLMClientFactory] Выбор LLM провайдера: {Config.LLM_PROVIDER}")
    if Config.LLM_PROVIDER.lower() == "gigachat":
        return GigaChatLLMClient()
    else:
        return OpenRouterLLMClient()
