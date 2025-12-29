import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks
from app.core.logger import logger
from app.db.database import db_manager
from app.services.message_handler import MessageHandler

app = FastAPI(title="WeChat Bot V2")
msg_handler = MessageHandler()


@app.on_event("startup")
async def startup_event():
    await db_manager.init_db()
    logger.info("🚀 机器人服务已启动")


@app.post("/callback")
async def callback(request: Request, background_tasks: BackgroundTasks):
    """
    接收 GeWeChat 回调
    """
    try:
        data = await request.json()
        # logger.debug(f"收到回调: {data}")

        # 使用 BackgroundTasks 异步处理，确保立即返回 200 给微信
        background_tasks.add_task(msg_handler.handle_incoming_message, data)

    except Exception as e:
        logger.error(f"Callback error: {e}")

    return {"ret": 200, "msg": "ok"}


if __name__ == "__main__":
    # 可以在这里直接运行调试
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)