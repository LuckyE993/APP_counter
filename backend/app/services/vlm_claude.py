import base64
import json
from typing import Dict, Any
from anthropic import AsyncAnthropic
from .vlm_base import VLMService
from ..config import settings

class ClaudeVLMService(VLMService):
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.VLM_API_KEY)
        self.model = settings.CLAUDE_MODEL

    async def parse_image(self, image_data: bytes, prompt: str) -> Dict[str, Any]:
        base64_image = base64.b64encode(image_data).decode('utf-8')

        message = await self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
        )

        content = message.content[0].text
        return json.loads(content)

    async def parse_text(self, text: str, prompt: str) -> Dict[str, Any]:
        message = await self.client.messages.create(
            model=self.model,
            max_tokens=300,
            messages=[
                {"role": "user", "content": f"{prompt}\n\n用户输入: {text}"}
            ]
        )

        content = message.content[0].text
        return json.loads(content)
