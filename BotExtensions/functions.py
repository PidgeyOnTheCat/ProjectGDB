import discord
from discord.ext import commands, tasks
from discord import app_commands

import requests, random
from pathlib import Path
from colorama import Fore

from datetime import datetime as dt
from dotenv import load_dotenv
import os

from BotVariables.lists import *
from BotVariables.version import botVersion


# Load environment variables
load_dotenv()
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
BOTDATA_FILE_PATH = os.getenv("BOTDATA_FILE_PATH")


class Functions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Get the ranks cog instance
        self.ranks_cog = self.bot.get_cog("Ranks")

        # Start XP task
        self.update_xp.start()

    # ---------------------------
    # Logging
    # ---------------------------
    @staticmethod
    def Log(type, username, message):
        logTypes = [
            Fore.GREEN + " INFO  " + Fore.RESET,
            Fore.YELLOW + "WARNING" + Fore.RESET,
            Fore.RED + " ERROR " + Fore.RESET,
            Fore.BLUE + " DEBUG " + Fore.RESET
        ]
        
        if username != None:
            print(f"[{Fore.LIGHTMAGENTA_EX}{dt.now().strftime('%d.%m.%Y')}{Fore.RESET}] [{Fore.LIGHTMAGENTA_EX}{dt.now().strftime('%H:%M:%S')}{Fore.RESET}] [ {logTypes[type]} ] [{Fore.LIGHTWHITE_EX}{username}{Fore.RESET}] {message}")
        else:
            print(f"[{Fore.LIGHTMAGENTA_EX}{dt.now().strftime('%d.%m.%Y')}{Fore.RESET}] [{Fore.LIGHTMAGENTA_EX}{dt.now().strftime('%H:%M:%S')}{Fore.RESET}] [ {logTypes[type]} ] {message}")


    # -------------------------
    # STARTUP BANNER
    # -------------------------
    @staticmethod
    async def startup_banner():
        print(
            rf"""
                {Fore.RED}.----------------. {Fore.GREEN}.----------------. {Fore.BLUE}.----------------.
                {Fore.RED}| .--------------. {Fore.GREEN}| .--------------. {Fore.BLUE}| .--------------. |
                {Fore.RED}| |    ______    | {Fore.GREEN}| |  ________    | {Fore.BLUE}| |   ______     | |
                {Fore.RED}| |  .' ___  |   | {Fore.GREEN}| | |_   ___ `.  | {Fore.BLUE}| |  |_   _ \    | |
                {Fore.RED}| | / .'   \_|   | {Fore.GREEN}| |   | |   `. \ | {Fore.BLUE}| |    | |_) |   | |
                {Fore.RED}| | | |    ____  | {Fore.GREEN}| |   | |    | | | {Fore.BLUE}| |    |  __'.   | |
                {Fore.RED}| | \ `.___]  _| | {Fore.GREEN}| |  _| |___.' / | {Fore.BLUE}| |   _| |__) |  | |
                {Fore.RED}| |  `._____.'   | {Fore.GREEN}| | |________.'  | {Fore.BLUE}| |  |_______/   | |
                {Fore.RED}| |              | {Fore.GREEN}| |              | {Fore.BLUE}| |              | |
                {Fore.RED}| '--------------' {Fore.GREEN}| '--------------' {Fore.BLUE}| '--------------' |
                {Fore.RED}'----------------' {Fore.GREEN}'----------------' {Fore.BLUE}'----------------'

                |  Made by: PidgeyCat | |  Version: {botVersion} | |  Discord: discord.gg/PBvj4AfUzr  |

    {Fore.RESET}
    """
        )

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

        # Fetch current stats
        userdata = await self.bot.db.get_user(member.id, guild.id)

        level = userdata["level"]
        xp = userdata["xp"]
        money = userdata["money"]

        # Add XP / Money based on variant
        if variant == 0: # normal text message
            xp_gain = random.randint(15, 35)
            money_gain = random.randint(20, 50)
            xp += xp_gain
            money += money_gain
            self.Log(0, member.name, f"+{xp_gain} xp | +{money_gain} money | message")
        elif variant == 1: # slash command
            xp_gain = random.randint(25, 40)
            money_gain = random.randint(30, 55)
            xp += xp_gain
            money += money_gain
            self.Log(0, member.name, f"+{xp_gain} xp | +{money_gain} money | command")
        elif variant == 2: # voice
            xp_gain = random.randint(25, 50)
            money_gain = random.randint(30, 65)
            xp += xp_gain
            money += money_gain
            self.Log(0, member.name, f"+{xp_gain} xp | +{money_gain} money | voice")
        elif variant == 3: # reaction
            xp_gain = random.randint(10, 30)
            money_gain = random.randint(15, 40)
            xp += xp_gain
            money += money_gain
            self.Log(0, member.name, f"+{xp_gain} xp | +{money_gain} money | reaction")
        await self.bot.db.execute(
            "UPDATE levels SET xp = ?, money = ? WHERE user = ? AND guild = ?",
            (xp, money, member.id, guild.id)
        )

        xp_required = (level + 1) * 100
        if xp >= xp_required:
            await self.levelup(member, guild)
        else:
            return

    async def levelup(self, member, guild, force=False):
        alerts_channel = self.bot.get_channel(1384275554718711858)

        # Fetch current stats
        userdata = await self.bot.db.get_user(member.id, guild.id)
        
        level = userdata["level"]
        xp = userdata["xp"]
        skillpoints = userdata["skillpoints"]

        xp_required = (level + 1) * 100

        # Level up
        level += 1

        if not force:
            xp -= xp_required
        else:
            xp = 0

        if level % 5 == 0:
            sp_gain = level // 5
            skillpoints += sp_gain
            await alerts_channel.send(f"**{member.name}** leveled up to **Level {level}** and gained **{sp_gain}** skill points!")
            self.Log(0, member.name, f"leveled up to {level} (+{sp_gain} SP)")
        else:
            await alerts_channel.send(f"**{member.name}** leveled up to **Level {level}**!")
            self.Log(0, member.name, f"leveled up to {level}")

        await self.bot.db.execute(
            "UPDATE levels SET level = ?, xp = ?, skillpoints = ? WHERE user = ? AND guild = ?",
            (level, xp, skillpoints, member.id, guild.id)
        )

        # Check for rankup
        await self.ranks_cog.rankup(member, guild)


    # ---------------------------
    # Rank Checks
    # ---------------------------
    @staticmethod
    def isOwner(interaction):
        return interaction.user.id == 650748710543687735
    
    @staticmethod
    def isAdmin(interaction):
        return interaction.user.guild_permissions.administrator
# ---------------------------
# Setup
# ---------------------------
async def setup(bot):
    await bot.add_cog(Functions(bot))
