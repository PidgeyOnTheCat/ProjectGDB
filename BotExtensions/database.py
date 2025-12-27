import aiosqlite
from pathlib import Path
import asyncio
import shutil

from BotExtensions.functions import *
from BotVariables.lists import *

class Database:
    def __init__(self, path: Path, backup_interval: int = Functions.hoursToSeconds(3), max_backups: int = 10):
        self.path = path
        self.db: aiosqlite.Connection | None = None
        self.backup_interval = backup_interval
        self.max_backups = max_backups
        self._backup_task: asyncio.Task | None = None

    async def connect(self):
        self.db = await aiosqlite.connect(self.path)
        self.db.row_factory = aiosqlite.Row
        await self.create_tables()
        # start the backup loop
        self._backup_task = asyncio.create_task(self._backup_loop())

    async def close(self):
        if self._backup_task:
            self._backup_task.cancel()
            try:
                await self._backup_task
            except asyncio.CancelledError:
                pass

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
    # USER HELPERS
    # -------------------------
    async def ensure_user(self, user_id: int, guild_id: int):
        """Ensures a user row exists. Safe to call anytime."""
        await self.execute(
            """
            INSERT INTO levels (user, guild)
            VALUES (?, ?)
            ON CONFLICT(user, guild) DO NOTHING
            """,
            (user_id, guild_id)
        )

    async def get_user(self, user_id: int, guild_id: int):
        """Guarantees the user exists, then returns their row."""
        await self.ensure_user(user_id, guild_id)
        return await self.fetchone(
            "SELECT * FROM levels WHERE user = ? AND guild = ?",
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

                cocksize DOUBLE NOT NULL DEFAULT 0,

                PRIMARY KEY (user, guild)
            )
            """
        )

    # -------------------------
    # BACKUP
    # -------------------------
    async def _backup_loop(self):
        while True:
            await asyncio.sleep(self.backup_interval)
            await self.create_backup()

    async def create_backup(self):
        if not self.path.exists():
            return

        # rotate old backups
        for i in range(self.max_backups - 1, 0, -1):
            old_backup = self.path.parent / f"{self.path.name}.bak{i}"
            new_backup = self.path.parent / f"{self.path.name}.bak{i+1}"
            if old_backup.exists():
                shutil.move(str(old_backup), str(new_backup))

        # create new backup as .bak1
        backup_path = self.path.parent / f"{self.path.name}.bak1"
        shutil.copy2(self.path, backup_path)

        Functions.Log(0, "Database backup created")
