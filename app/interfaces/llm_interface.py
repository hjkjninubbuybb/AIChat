from abc import ABC, abstractmethod
from typing import List, Dict

class LLMInterface(ABC):
    @abstractmethod
    async def chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """发送对话并获取回复"""
        pass