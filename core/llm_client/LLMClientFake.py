from core.llm_client.LLMClientBase import LLMClientBase

class LLMClientBaseFake(LLMClientBase):
    async def send_message(self, message, prompt_type=None):
        return {"text": "Fake response"}