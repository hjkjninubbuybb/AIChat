from abc import ABC, abstractmethod

class TTSInterface(ABC):
    @abstractmethod
    async def text_to_voice(self, text: str, output_dir: str) -> str:
        """将文字转换为音频文件，返回文件路径"""
        pass