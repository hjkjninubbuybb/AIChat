from abc import ABC, abstractmethod

class ASRInterface(ABC):
    @abstractmethod
    async def voice_to_text(self, audio_file_path: str) -> str:
        """将音频文件转换为文字"""
        pass