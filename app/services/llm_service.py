from typing import List, Dict
from openai import AsyncOpenAI
from app.interfaces.llm_interface import LLMInterface
from app.core.config import settings
from app.core.logger import logger

class SiliconFlowService(LLMInterface):
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.SILICON_API_KEY,
            base_url=settings.SILICON_BASE_URL
        )

    async def chat_completion(self, messages: List[Dict[str, str]]) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=messages,
                temperature=1.3, # 高温度更拟人
                max_tokens=512
            )
            content = response.choices[0].message.content
            logger.info(f"AI回复: {content[:30]}...")
            return content
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            return "（大脑过载中...）"