from core.llm_client.LLMClientBase import BaseLLMClient

class FakeLLMClient(BaseLLMClient):
    async def send_message(self, message, prompt_type=None):
        return {"text": "Fake response"}