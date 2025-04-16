class FakeLLMClient:
    async def send_message(self, message, prompt_type=None):
        return {"text": "Fake response"}