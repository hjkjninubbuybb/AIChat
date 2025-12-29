import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # AI 配置
    SILICON_API_KEY: str
    SILICON_BASE_URL: str = "https://api.siliconflow.cn/v1"
    LLM_MODEL: str = "Qwen/Qwen2.5-7B-Instruct"
    GROQ_API_KEY: str

    # 微信配置
    GEWE_API_URL: str = "http://localhost:2531/v2/api"
    CALLBACK_URL: str = "http://bot-app:8000/callback"

    # 路径配置 (自动获取项目根目录)
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    TEMP_AUDIO_DIR: str = os.path.join(DATA_DIR, "temp_audio")

    # 数据库路径
    DB_PATH: str = os.path.join(DATA_DIR, "chat_memory.db")

    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 实例化配置对象
settings = Settings()

# 确保目录存在
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.TEMP_AUDIO_DIR, exist_ok=True)