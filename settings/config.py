# settings/config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_API_BASE = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
    LLM_MODEL = os.getenv("LLM_MODEL", "deepseek/deepseek-r1-zero:free")
    # Параметр для выбора LLM-провайдера; допустимые значения, например: "openrouter" или "gigachat"
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter")

    # Настройки для GigaChat (если потребуется)
    GIGACHAT_API_KEY = os.getenv("GIGACHAT_API_KEY")
    GIGACHAT_API_BASE = os.getenv("GIGACHAT_API_BASE", "https://api.gigachat.example.com/v1")
    GIGACHAT_MODEL = os.getenv("GIGACHAT_MODEL", "gigachat/gigachat-model")
