import base64
import json
from typing import Dict, Any
from openai import AsyncOpenAI
from .vlm_base import VLMService
from ..config import settings

class OpenAIVLMService(VLMService):
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.VLM_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        self.model = settings.OPENAI_MODEL

    async def parse_image(self, image_data: bytes, prompt: str) -> Dict[str, Any]:
        base64_image = base64.b64encode(image_data).decode('utf-8')

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=5000
        )

        content = response.choices[0].message.content
        # 清理markdown代码块标记
        content = content.strip()
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        return json.loads(content)

    async def parse_text(self, text: str, prompt: str) -> Dict[str, Any]:
        print({"text": text, "prompt": prompt})
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": f"{prompt}\n\n用户输入: {text}"}
            ],
            max_tokens=3000
        )

        content = response.choices[0].message.content
        print(content)
        # 清理markdown代码块标记
        content = content.strip()
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        return json.loads(content)
