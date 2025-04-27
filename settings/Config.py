# settings/Config.py

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="D:/Tools/.env")

class Config:
    #--- LLM-провайдер: -----------------------------------------------------
    # LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter")
    # LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mockllm")


    #--- OpenRouter settings: --------------------------------------------
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_API_BASE = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
    OPENROUTER_LLM_MODEL = os.getenv("LLM_MODEL", "deepseek/deepseek-r1-zero:free")

    #--- Gemini settings: --------------------------------------------
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")  # Актуальное название модели


    #--- GigaChat settings: -------------------------------------------
    GIGACHAT_API_KEY = os.getenv("GIGACHAT_API_KEY")
    GIGACHAT_API_BASE = os.getenv("GIGACHAT_API_BASE", "https://api.gigachat.example.com/v1")
    GIGACHAT_MODEL = os.getenv("GIGACHAT_MODEL", "gigachat/gigachat-model")
