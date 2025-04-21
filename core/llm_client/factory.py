# core/llm_client/factory.py

import logging
from settings.config import Config
from core.llm_client.LLMClientBase import BaseLLMClient
from core.llm_client.OpenRouterLLMClient import OpenRouterLLMClient
from core.llm_client.FakeLLMClient import FakeLLMClient
from core.llm_client.MockLLMClient import MockLLMClient

# from core.llm_client.gigachat import GigaChatLLMClient

logger = logging.getLogger("ai_agent.core.llm_client.factory")


def get_llm_client() -> BaseLLMClient:
    logger.info(f"[LLMClientFactory] Выбор LLM провайдера: {Config.LLM_PROVIDER}")
    if Config.LLM_PROVIDER.lower() == "gigachat":
        return FakeLLMClient()
    elif Config.LLM_PROVIDER.lower() == "openrouter":
        return OpenRouterLLMClient()
    elif Config.LLM_PROVIDER.lower() == "mockllm":
        return MockLLMClient(debug=True)
