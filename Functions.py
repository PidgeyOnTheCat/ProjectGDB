import discord
from discord.ext import commands, tasks
from discord import app_commands

import requests, random, asyncio
from pathlib import Path

from lists import logTypes
from datetime import datetime as dt
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
BOTDATA_FILE_PATH = os.getenv("BOTDATA_FILE_PATH")


class Functions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Start XP task
        self.update_xp.start()

        # Ensure database is initialized
        if not hasattr(bot, "db"):
            from database import Database  # Import your Database class
            bot.db = Database(Path(BOTDATA_FILE_PATH) / "stats.db")
            self.bot.loop.create_task(bot.db.connect())

    # ---------------------------
    # Logging
    # ---------------------------
    @staticmethod
    def Log(type, message):
        try:
            print(f"[{dt.now().strftime('%d.%m.%Y')}] [{dt.now().strftime('%H:%M:%S')}] [ {logTypes[type]} ] {message}")
        except Exception as e:
            print(f"Error logging message: {e}")

    # ---------------------------
    # API Utility Functions
    # ---------------------------
    @staticmethod
    def get_truth():
        data = requests.get("https://api.truthordarebot.xyz/v1/truth").json()
        return data.get("question")

    @staticmethod
    def get_dare():
        data = requests.get("https://api.truthordarebot.xyz/v1/dare").json()
        return data.get("question")

    @staticmethod
    def get_wyr():
        data = requests.get("https://api.truthordarebot.xyz/v1/wyr").json()
        return data.get("question")

    @staticmethod
    def get_funny():
        data = requests.get("https://api.humorapi.com/memes").json()
        memes = data.get("memes", [])
        return random.choice(memes)["url"] if memes else None

    @staticmethod
    def get_insult():
        data = requests.get("https://evilinsult.com/generate_insult.php?lang=en&type=json").json()
        return data.get("insult")

    @staticmethod
    def get_steamid64(vanity_url):
        base_url = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/"
        params = {"key": STEAM_API_KEY, "vanityurl": vanity_url}
        data = requests.get(base_url, params=params).json()
        return data["response"]["steamid"] if data["response"]["success"] == 1 else None

    @staticmethod
    def convert_url(url):
        if "steamcommunity.com/profiles/" in url:
            return url.rstrip("/").split("/")[-1]
        elif "steamcommunity.com/id/" in url:
            vanity = url.rstrip("/").split("/")[-1]
            return Functions.get_steamid64(vanity)
        return None

    @staticmethod
    def hoursToSeconds(hours):
        return hours * 3600

    @staticmethod
    def timeConvert(seconds):
        seconds = int(round(seconds))
        if seconds < 0:
            return "Invalid"
        h, m, s = seconds // 3600, (seconds % 3600) // 60, seconds % 60
        if h > 0:
            return f"{h} hours, {m} minutes and {s} seconds" if h != 1 else f"{h} hour, {m} minutes and {s} seconds"
        elif m > 0:
            return f"{m} minutes and {s} seconds"
        return f"{s} seconds"

    # ---------------------------
    # XP Task
    # ---------------------------
    @tasks.loop(minutes=1.0)
    async def update_xp(self):
        for guild in self.bot.guilds:
            for channel in guild.voice_channels:
                for member in channel.members:
                    if not member.bot:
                        await self.give_xp(member, guild, 2)

    # ---------------------------
    # Give XP / Money
    # ---------------------------
    async def give_xp(self, member, guild, variant):

        # Ensure user exists
        await self.bot.db.execute(
            """
            INSERT INTO levels (user, guild)
            VALUES (?, ?)
            ON CONFLICT(user, guild) DO NOTHING
            """,
            (member.id, guild.id)
        )

        # Fetch stats
        result = await self.bot.db.fetchone(
            "SELECT xp, level, money, bank, nword, skillpoints FROM levels WHERE user = ? AND guild = ?",
            (member.id, guild.id)
        )

        if result:
            xp, level, money, bank, nword, skillpoints = result
        else:
            xp = level = money = bank = nword = skillpoints = 0

        # Add XP / Money based on variant
        if variant == 0:
            xp += random.randint(15, 35)
            money += random.randint(20, 50)
            self.Log(0, f"[{member.name}] got XP and money")
        elif variant == 1:
            xp += random.randint(25, 40)
            money += random.randint(30, 55)
            self.Log(0, f"[{member.name}] got XP and money")
        elif variant == 2:
            xp += random.randint(25, 50)
            money += random.randint(30, 65)
            self.Log(0, f"[{member.name}] got XP and money in vc")

        await self.bot.db.execute(
            "UPDATE levels SET xp = ?, money = ? WHERE user = ? AND guild = ?",
            (xp, money, member.id, guild.id)
        )

        xp_required = (level + 1) * 100
        if xp >= xp_required:
            await self.levelup(member, guild)
        else:
            return

    async def levelup(self, member, guild):
        alerts_channel = self.bot.get_channel(1384275554718711858)

        # Ensure user exists
        await self.bot.db.execute(
            """
            INSERT INTO levels (user, guild)
            VALUES (?, ?)
            ON CONFLICT(user, guild) DO NOTHING
            """,
            (member.id, guild.id)
        )

        # Fetch stats
        result = await self.bot.db.fetchone(
            "SELECT xp, level, money, bank, nword, skillpoints FROM levels WHERE user = ? AND guild = ?",
            (member.id, guild.id)
        )

        if result:
            xp, level, money, bank, nword, skillpoints = result
        else:
            xp = level = money = bank = nword = skillpoints = 0
        
        # Level up
        level += 1
        xp = 0
        if level % 5 == 0:
            sp_gain = level // 5
            skillpoints += sp_gain
            await alerts_channel.send(f"**{member.name}** has leveled up to **{level}** and gained **{sp_gain}** skill points!")
            self.Log(0, f"[{member.name}] leveled up to {level} (+{sp_gain} SP)")
        else:
            await alerts_channel.send(f"**{member.name}** has leveled up to **{level}**!")
            self.Log(0, f"[{member.name}] leveled up to {level}")

        await self.bot.db.execute(
            "UPDATE levels SET level = ?, xp = ?, skillpoints = ? WHERE user = ? AND guild = ?",
            (level, xp, skillpoints, member.id, guild.id)
        )

# ---------------------------
# Setup
# ---------------------------
async def setup(bot):
    await bot.add_cog(Functions(bot))
