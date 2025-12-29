import os
import uuid
import edge_tts
from groq import Groq
from app.interfaces.asr_interface import ASRInterface
from app.interfaces.tts_interface import TTSInterface
from app.core.config import settings
from app.core.logger import logger


class GroqASRService(ASRInterface):
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    async def voice_to_text(self, audio_file_path: str) -> str:
        if not os.path.exists(audio_file_path):
            return ""
        try:
            with open(audio_file_path, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                    file=(os.path.basename(audio_file_path), file.read()),
                    model="whisper-large-v3",
                    response_format="json",
                    language="zh"
                )
            text = transcription.text.strip()
            logger.info(f"语音转字结果: {text}")
            return text
        except Exception as e:
            logger.error(f"ASR失败: {e}")
            return ""


class EdgeTTSService(TTSInterface):
    def __init__(self, voice: str = "zh-CN-XiaoxiaoNeural"):
        self.voice = voice

    async def text_to_voice(self, text: str, output_dir: str) -> str:
        # 清理文本
        clean_text = text.replace("[语音]", "").strip()
        if not clean_text:
            return ""

        filename = f"{uuid.uuid4()}.mp3"
        output_path = os.path.join(output_dir, filename)

        try:
            communicate = edge_tts.Communicate(clean_text, self.voice)
            await communicate.save(output_path)
            logger.info(f"语音生成成功: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"TTS失败: {e}")
            return ""