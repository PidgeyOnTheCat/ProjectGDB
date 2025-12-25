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

    def _check(self):
        if not self.db:
            raise RuntimeError("Database not connected")

    async def execute(self, query: str, params=()):
        self._check()
        async with self.db.cursor() as cursor:
            await cursor.execute(query, params)
        await self.db.commit()

    async def fetchone(self, query: str, params=()):
        self._check()
        async with self.db.cursor() as cursor:
            await cursor.execute(query, params)
            return await cursor.fetchone()

    async def fetchall(self, query: str, params=()):
        self._check()
        async with self.db.cursor() as cursor:
            await cursor.execute(query, params)
            return await cursor.fetchall()

    # -------------------------
    # USER HELPERS (THIS IS THE MAGIC)
    # -------------------------

    async def ensure_user(self, user_id: int, guild_id: int):
        """
        Ensures a user row exists. Safe to call anytime.
        """
        await self.execute(
            """
            INSERT INTO levels (user, guild)
            VALUES (?, ?)
            ON CONFLICT(user, guild) DO NOTHING
            """,
            (user_id, guild_id)
        )

    async def get_user(self, user_id: int, guild_id: int):
        """
        Guarantees the user exists, then returns their row.
        """
        await self.ensure_user(user_id, guild_id)

        return await self.fetchone(
            """
            SELECT *
            FROM levels
            WHERE user = ? AND guild = ?
            """,
            (user_id, guild_id)
        )

    # -------------------------
    # TABLE CREATION
    # -------------------------

    async def create_tables(self):
        await self.execute(
            """
            CREATE TABLE IF NOT EXISTS levels (
                user INTEGER NOT NULL,
                guild INTEGER NOT NULL,

                level INTEGER NOT NULL DEFAULT 0,
                xp INTEGER NOT NULL DEFAULT 0,
                money INTEGER NOT NULL DEFAULT 0,
                bank INTEGER NOT NULL DEFAULT 0,
                nword INTEGER NOT NULL DEFAULT 0,
                skillpoints INTEGER NOT NULL DEFAULT 0,

                skill_robfull_lvl INTEGER NOT NULL DEFAULT 0,
                skill_robchance_lvl INTEGER NOT NULL DEFAULT 0,
                skill_heistchance_lvl INTEGER NOT NULL DEFAULT 0,
                skill_banksecurity_lvl INTEGER NOT NULL DEFAULT 0,

                PRIMARY KEY (user, guild)
            )
            """
        )
