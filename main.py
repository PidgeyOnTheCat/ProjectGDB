import discord
import os
import asyncio
from pathlib import Path
from discord.ext import commands
from dotenv import load_dotenv
from colorama import Fore as f

from BotExtensions.database import Database
from BotExtensions.functions import Functions
from BotVariables.version import botVersion


# -------------------------
# ENV SETUP
# -------------------------
load_dotenv()
TOKEN = os.getenv("TOKEN")
BOTDATA_FILE_PATH = os.getenv("BOTDATA_FILE_PATH")

if not TOKEN:
    raise RuntimeError("TOKEN not found in .env")
if not BOTDATA_FILE_PATH:
    raise RuntimeError("BOTDATA_FILE_PATH not found in .env")


# -------------------------
# CUSTOM BOT CLASS
# -------------------------
class MyBot(commands.Bot):
    async def setup_hook(self):
        # -------------------------
        # DATABASE (LOAD ONCE)
        # -------------------------
        db_path = Path(BOTDATA_FILE_PATH) / "stats.db"
        self.db = Database(db_path)
        try:
            await self.db.connect()
            print(f"{f.GREEN}[DB] Database connected{f.RESET}")
        except Exception as e:
            print(f"{f.RED}[DB] Database failed connect: {e}{f.RESET}")

        # -------------------------
        # LOAD EXTENSIONS
        # -------------------------
        extensions = [
            "BotExtensions.errorhandler",
            "BotExtensions.ranks",
            "BotExtensions.functions",
            "BotExtensions.economy",
            "BotExtensions.uncathegorized",
            "BotExtensions.voice",
            "BotExtensions.console",
            "BotExtensions.chatcommands",
            "BotExtensions.leaderboards",
            "BotExtensions.skills",
            # "BotExtensions.website",
        ]

        for ext in extensions:
            try:
                await self.load_extension(ext)
                print(f"{f.GREEN}[EXT] Loaded {ext}{f.RESET}")
            except Exception as e:
                print(f"{f.RED}[EXT] Failed to load {ext}: {e}{f.RESET}")

    async def close(self):
        # Graceful shutdown
        if hasattr(self, "db"):
            await self.db.close()
            print(f"{f.GREEN}[DB] Database closed{f.RESET}")

        await super().close()


# -------------------------
# BOT INSTANCE
# -------------------------
intents = discord.Intents.all()
bot = MyBot(command_prefix=">", intents=intents)


# -------------------------
# READY EVENT (LOGGING ONLY)
# -------------------------
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print("---------------------------------")
        print(f"Successfully synced {len(synced)} commands.")
        print(
            f"Logged in as {bot.user}\n"
            f"Bot version: {botVersion}\n"
            "_________________________________"
        )
    except Exception as e:
        print("Failed to sync commands:", e)


# -------------------------
# MAIN ENTRY POINT
# -------------------------
async def main():
    await Functions.startup_banner()
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
