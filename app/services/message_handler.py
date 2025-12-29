import os
import httpx
import uuid
from app.core.logger import logger
from app.core.config import settings
from app.services.llm_service import SiliconFlowService
from app.services.voice_service import GroqASRService, EdgeTTSService
from app.services.chat_history_service import ChatHistoryService
from app.services.wechat_service import WeChatClient


class MessageHandler:
    def __init__(self):
        self.llm = SiliconFlowService()
        self.asr = GroqASRService()
        self.tts = EdgeTTSService()
        self.wechat = WeChatClient()

        # --- 核心人设 ---
        self.system_prompt = """
        # Role
        你叫“小野”，22岁，真实人类，性格随性、毒舌、爱玩梗。
        # Rules
        1. 绝不使用机器人口吻，像真实人类一样聊天。
        2. 回复简短（15字以内），除非讲故事。
        3. 不用标点符号，用空格代替。
        4. 如果用户发语音，或者你觉得适合发语音，可以用 [语音] 开头。
        5. 不要每句话都回，偶尔可以回个表情包（用文字描述 [表情:xxx]）。
        """

    async def handle_incoming_message(self, msg_data: dict):
        try:
            # 简单解析 GeWeChat 回调格式
            # 注意：需根据 GeWeChat 实际日志调整字段
            wxid = msg_data.get("FromUserName")
            msg_type = msg_data.get("MsgType")
            content = msg_data.get("Content")

            # 过滤不需要的消息
            if not wxid or "chatroom" in wxid:
                return  # 暂时不回群聊

            user_text = ""
            is_voice_in = False

            # 处理文本
            if msg_type == "Text":
                user_text = content
            # 处理语音
            elif msg_type == "Voice":
                voice_url = msg_data.get("Url")  # 假设 GeWeChat 返回 URL
                # 如果没有 Url，可能需要调用 getMsg 接口，这里简化处理
                if voice_url:
                    logger.info("下载语音中...")
                    temp_path = os.path.join(settings.TEMP_AUDIO_DIR, f"{uuid.uuid4()}.mp3")
                    async with httpx.AsyncClient() as client:
                        resp = await client.get(voice_url)
                        if resp.status_code == 200:
                            with open(temp_path, "wb") as f:
                                f.write(resp.content)
                            user_text = await self.asr.voice_to_text(temp_path)
                            is_voice_in = True
                            os.remove(temp_path)  # 清理

            if not user_text:
                return

            logger.info(f"用户({wxid})说: {user_text}")

            # 1. 存入用户消息
            await ChatHistoryService.add_message(wxid, "user", user_text)

            # 2. 获取上下文
            context = await ChatHistoryService.get_recent_context(wxid)
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(context)

            # 3. AI 思考
            ai_reply = await self.llm.chat_completion(messages)

            # 4. 存入 AI 回复
            await ChatHistoryService.add_message(wxid, "assistant", ai_reply)

            # 5. 决策回复方式
            should_reply_voice = is_voice_in or "[语音]" in ai_reply
            clean_text = ai_reply.replace("[语音]", "").strip()

            if should_reply_voice:
                logger.info("生成语音回复...")
                audio_path = await self.tts.text_to_voice(clean_text, settings.TEMP_AUDIO_DIR)
                if audio_path:
                    await self.wechat.send_file(wxid, audio_path)
                else:
                    await self.wechat.send_text(wxid, clean_text)
            else:
                await self.wechat.send_text(wxid, clean_text)

        except Exception as e:
            logger.error(f"处理消息异常: {e}")