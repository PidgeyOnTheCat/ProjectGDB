import aiosqlite
from pathlib import Path

class Database:
    def __init__(self, path: Path):
        self.path = path
        self.db: aiosqlite.Connection | None = None

    async def connect(self):
        self.db = await aiosqlite.connect(self.path)
        self.db.row_factory = aiosqlite.Row
        await self.create_tables()

    async def close(self):
        if self.db:
            await self.db.close()

    async def execute(self, query: str, params=()):
        async with self.db.cursor() as cursor:
            await cursor.execute(query, params)
        await self.db.commit()

    async def fetchone(self, query: str, params=()):
        async with self.db.cursor() as cursor:
            await cursor.execute(query, params)
            return await cursor.fetchone()

    async def fetchall(self, query: str, params=()):
        async with self.db.cursor() as cursor:
            await cursor.execute(query, params)
            return await cursor.fetchall()

    # -------------------------
    # TABLE CREATION / MIGRATION
    # -------------------------
    async def create_tables(self):
        await self.execute("""
        CREATE TABLE IF NOT EXISTS levels (
            level INTEGER, 
            xp INTEGER, 
            money INTEGER, 
            bank INTEGER, 
            user INTEGER, 
            guild INTEGER, 
            nword INTEGER, 
            skillpoints INTEGER, 
            skill_robfull_lvl INTEGER, 
            skill_robchance_lvl INTEGER, 
            skill_heistchance_lvl INTEGER,
            skill_banksecurity_lvl INTEGER,
            UNIQUE(user, guild)
        )
        """)
