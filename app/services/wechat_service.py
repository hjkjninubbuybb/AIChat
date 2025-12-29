import httpx
from app.core.config import settings
from app.core.logger import logger


class WeChatClient:
    def __init__(self):
        self.api_url = settings.GEWE_API_URL

    async def send_text(self, wxid: str, content: str):
        url = f"{self.api_url}/message/text"
        payload = {"toWxid": wxid, "content": content}
        async with httpx.AsyncClient() as client:
            try:
                await client.post(url, json=payload)
            except Exception as e:
                logger.error(f"发送文本失败: {e}")

    async def send_file(self, wxid: str, local_file_path: str):
        # 注意：这里假设 Docker 路径映射一致
        # 如果是本地 Windows 运行，GeWeChat 在 Docker，需要确保 Docker 能访问这个路径
        # 或者使用 HTTP URL 方式传文件。这里为了简单演示，假设共享卷挂载
        filename = local_file_path.split(os.sep)[-1]
        container_path = f"/root/temp_audio/{filename}"  # 对应 Docker 里的路径

        url = f"{self.api_url}/message/file"
        payload = {"toWxid": wxid, "fileUrl": container_path}

        async with httpx.AsyncClient() as client:
            try:
                await client.post(url, json=payload)
            except Exception as e:
                logger.error(f"发送文件失败: {e}")