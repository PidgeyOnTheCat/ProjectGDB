import discord
import os
import asyncio
from pathlib import Path
from discord.ext import commands
from dotenv import load_dotenv
from colorama import Fore as f

from BotVariables.version import botVersion
from BotExtensions.database import Database

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
        await self.db.connect()

        print("[DB] Database connected")

        # -------------------------
        # LOAD EXTENSIONS
        # -------------------------
        extensions = [
            "BotExtensions.ranks",
            "BotExtensions.functions",
            "BotExtensions.economy",
            "BotExtensions.uncathegorized",
            "BotExtensions.voice",
            "BotExtensions.console",
            "BotExtensions.chatcommands",
            "BotExtensions.leaderboards",
            "BotExtensions.skills",
        ]

        for ext in extensions:
            try:
                await self.load_extension(ext)
                print(f"[EXT] Loaded {ext}")
            except Exception as e:
                print(f"[EXT] Failed to load {ext}: {e}")

    async def close(self):
        # Graceful shutdown
        if hasattr(self, "db"):
            await self.db.close()
            print("[DB] Database closed")

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
# STARTUP BANNER
# -------------------------
async def startup_banner():
    print(
        rf"""
            {f.RED}.----------------. {f.GREEN}.----------------. {f.BLUE}.----------------.
            {f.RED}| .--------------. {f.GREEN}| .--------------. {f.BLUE}| .--------------. |
            {f.RED}| |    ______    | {f.GREEN}| |  ________    | {f.BLUE}| |   ______     | |
            {f.RED}| |  .' ___  |   | {f.GREEN}| | |_   ___ `.  | {f.BLUE}| |  |_   _ \    | |
            {f.RED}| | / .'   \_|   | {f.GREEN}| |   | |   `. \ | {f.BLUE}| |    | |_) |   | |
            {f.RED}| | | |    ____  | {f.GREEN}| |   | |    | | | {f.BLUE}| |    |  __'.   | |
            {f.RED}| | \ `.___]  _| | {f.GREEN}| |  _| |___.' / | {f.BLUE}| |   _| |__) |  | |
            {f.RED}| |  `._____.'   | {f.GREEN}| | |________.'  | {f.BLUE}| |  |_______/   | |
            {f.RED}| |              | {f.GREEN}| |              | {f.BLUE}| |              | |
            {f.RED}| '--------------' {f.GREEN}| '--------------' {f.BLUE}| '--------------' |
            {f.RED}'----------------' {f.GREEN}'----------------' {f.BLUE}'----------------'

            |  Made by: PidgeyCat | |  Version: {botVersion} | |  Discord: discord.gg/PBvj4AfUzr  |

{f.RESET}
"""
    )


# -------------------------
# MAIN ENTRY POINT
# -------------------------
async def main():
    await startup_banner()
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
