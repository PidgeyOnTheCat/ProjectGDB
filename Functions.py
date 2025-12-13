# This file contains functions that are used in the bot.
# It includes functions for getting truths, dares, would you rather questions, memes, insults, and converting Steam URLs to SteamID64.
import discord
from discord.ext import commands, tasks
from discord import app_commands

import requests, random, aiosqlite, asyncio
from pathlib import Path

from lists import logTypes

from datetime import datetime as dt

from dotenv import load_dotenv
import os

# Load the environment variables
load_dotenv()
# Load data from the .env file
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
BOTDATA_FILE_PATH = os.getenv("BOTDATA_FILE_PATH")

class Functions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Functions.py has loaded successfully")

        # level database stuff
        setattr(self.bot, "db", await aiosqlite.connect(Path(BOTDATA_FILE_PATH) / "stats.db"))
        await asyncio.sleep(3)
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
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
                    skill_banksecurity_lvl INTEGER
                )
                """
            )

    # Main functions
    def Log(type, message):
        try:
            print(f"[{dt.now().strftime('%H:%M:%S')}] [ {logTypes[type]} ] {message}")
        except Exception as e:
            print(f"Error logging message: {e}")

    def get_truth():
        # Send a GET request to the API
        response = requests.get("https://api.truthordarebot.xyz/v1/truth")

        # Parse the JSON response
        data = response.json()

        # Extract the truth question
        question = data["question"]

        # Return the truth question to the function
        return(question)

    def get_dare():
        # Send a GET request to the API
        response = requests.get("https://api.truthordarebot.xyz/v1/dare")

        # Parse the JSON response
        data = response.json()

        # Extract the truth question
        question = data["question"]

        # Return the truth question to the function
        return(question)

    def get_wyr():
        # Send GET request to the API
        response = requests.get("https://api.truthordarebot.xyz/v1/wyr")

            # Parse the JSON response
        data = response.json()

        # Extract the truth question
        question = data["question"]

        # Return the truth question to the function
        return(question)

    def get_funny():
        # Send a GET request to the API
        response = requests.get("https://api.humorapi.com/memes")
        
        # Parse the JSON response
        data = response.json()

        # Extract the 'memes' array from the JSON
        memes = data["memes"]
        
        # Randomly choose a meme from the array
        random_meme = random.choice(memes)

        # Get the URL of the meme
        meme_url = random_meme["url"]

        return meme_url

    def get_insult():
        response = requests.get("https://evilinsult.com/generate_insult.php?lang=en&type=json")
        data = response.json()
        insult = data.get("insult")
        return insult

    def get_steamid64(vanity_url):
        api_key = STEAM_API_KEY  # Replace with your actual Steam API key
        base_url = 'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/'
        params = {
            'key': api_key,
            'vanityurl': vanity_url
        }
        
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if data['response']['success'] == 1:
            return data['response']['steamid']
        else:
            return None

    def convert_url(url):
        api_key = STEAM_API_KEY  # Replace with your actual Steam API key
        if 'steamcommunity.com/profiles/' in url:
            # Extract the SteamID64 directly from the URL
            steamid64 = url.split('/')[-1] if url.endswith('/') else url.split('/')[-1]
        elif 'steamcommunity.com/id/' in url:
            # Extract the vanity URL and resolve to SteamID64
            vanity_url = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
            steamid64 = Functions.get_steamid64(vanity_url)
        else:
            steamid64 = None
        
        return steamid64

    def hoursToSeconds(hours):
        return hours * 60 * 60

    def timeConvert(x):
        # Round Seconds to integer
        x = int(round(x))

        if x < 0:
            return "Invalid"
        elif x < 60:
            return f"{x} seconds"
        elif x < 3600:
            minutes = x // 60
            seconds = x % 60
            return f"{minutes} minutes and {seconds} seconds"
        else:
            hours = x // 3600
            minutes = (x % 3600) // 60
            seconds = x % 60
            if hours == 1:
                return f"{hours} hour, {minutes} minutes and {seconds} seconds"
            else:
                return f"{hours} hours, {minutes} minutes and {seconds} seconds"
            
    async def caca(self):
        self.Log(0, "Caca function called")
            
    # Make users in voice calls get xp every minute
    @tasks.loop(minutes=1.0)
    async def update_xp(self):
        for guild in self.bot.guilds:
            for voice_channel in guild.voice_channels:
                for member in voice_channel.members:
                    if not member.bot:
                        await self.give_xp(member, guild, 2)

    async def give_xp(self, member, guild, variant):
        alerts_channel = self.bot.get_channel(1384275554718711858)

        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT xp, level, money, bank, nword, skillpoints FROM levels WHERE user = ? AND guild = ?", (member.id, guild.id))
            result = await cursor.fetchone()
            
            if not result:
                await cursor.execute("INSERT INTO levels (level, xp, money, bank, user, guild, nword, skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl, skill_banksecurity_lvl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (0, 0, 0, 0, member.id, guild.id, 0, 0, 0, 0, 0, 0))
                await self.bot.db.commit()
                xp = 0
                level = 0
                money = 0
                bank = 0
                nword = 0
                skillpoints = 0
            else:
                xp, level, money, bank, nword, skillpoints = result

            if variant == 0: # normal message
                xp += random.randint(15, 35) # 15, 40 / 100, 10000   per give
                money += random.randint(20, 50) # 20, 55 / 1000, 10000   per give
            elif variant == 1: # slash command
                xp += random.randint(25, 40) # 25, 40 / 100, 10000   per give
                money += random.randint(30, 55) # 30, 55 / 1000, 10000   per give
            elif variant == 2: # vc
                xp += random.randint(25, 50) # 25, 40 / 100, 10000   per give
                money += random.randint(30, 65) # 30, 55 / 1000, 10000   per give

            await cursor.execute("UPDATE levels SET xp = ?, money = ? WHERE user = ? AND guild = ?", (xp, money, member.id, guild.id))

            # Calculate xp needed for level up
            xp_required = (level + 1) * 100

            if xp >= xp_required:
                level += 1
                xp = 0 # Reset XP after level up

                if level % 5 == 0:
                    skillpointsamount = level / 5
                    skillpointsamount = int(skillpointsamount)
                    skillpoints += skillpointsamount
                    await alerts_channel.send(f"{member.mention} has leveled up to level **{level}** and has gained **{skillpointsamount}** skill points!")
                    Functions.Log(0, f"{member.name} leveled up to {level} got {skillpointsamount}")
                else:
                    await alerts_channel.send(f"{member.mention} has leveled up to level **{level}**!")
                    Functions.Log(0, f"{member.name} leveled up to {level}")

                await cursor.execute("UPDATE levels SET level = ?, xp = ?, skillpoints = ? WHERE user = ? AND guild = ?", (level, xp, skillpoints, member.id, guild.id))

            await self.bot.db.commit()
            Functions.Log(0, f"XP and money given to {member.name}")
    
    @app_commands.command(name="testdb", description="Test the database connection")
    async def testdb(self, interaction: discord.Interaction):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT sqlite_version();")
                version = await cursor.fetchone()
                await interaction.response.send_message(f"Database connection successful! SQLite version: {version[0]}")
                self.Log(0, f"Database connection successful! SQLite version: {version[0]}")
        except Exception as e:
            await interaction.response.send_message(f"Database connection failed: {str(e)}")
            self.Log(2, f"Database connection failed: {str(e)}")

async def setup(bot):
    await bot.add_cog(Functions(bot))