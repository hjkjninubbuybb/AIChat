import aiosqlite
from app.core.config import settings
from app.core.logger import logger

class Database:
    def __init__(self):
        self.db_path = settings.DB_PATH

    async def init_db(self):
        logger.info(f"正在初始化数据库: {self.db_path}")
        async with aiosqlite.connect(self.db_path) as db:
            # 创建聊天记录表
            await db.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    wxid TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("CREATE INDEX IF NOT EXISTS idx_wxid ON chat_history(wxid)")
            await db.commit()
            logger.info("数据库初始化完成")

# 全局数据库实例
db_manager = Database()