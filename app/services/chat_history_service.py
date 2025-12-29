import aiosqlite
from typing import List, Dict
from app.db.database import db_manager

class ChatHistoryService:
    @staticmethod
    async def add_message(wxid: str, role: str, content: str):
        async with aiosqlite.connect(db_manager.db_path) as db:
            await db.execute(
                "INSERT INTO chat_history (wxid, role, content) VALUES (?, ?, ?)",
                (wxid, role, content)
            )
            await db.commit()

    @staticmethod
    async def get_recent_context(wxid: str, limit: int = 6) -> List[Dict[str, str]]:
        async with aiosqlite.connect(db_manager.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT role, content FROM chat_history WHERE wxid = ? ORDER BY id DESC LIMIT ?",
                (wxid, limit)
            ) as cursor:
                rows = await cursor.fetchall()
                # 反转顺序，让旧消息在前
                return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]