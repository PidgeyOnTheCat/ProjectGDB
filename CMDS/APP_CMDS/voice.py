import random

import discord
from discord.ext import commands
from discord import app_commands

from Functions import *
from lists import *
from config import *

import aiosqlite, asyncio, random

import openai
openai.api_key = OPENAI_API_KEY

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("voice.py has loaded succesfully")

        # level database stuff
        setattr(self.bot, "db", await aiosqlite.connect("BotData/stats.db"))
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
                    skill_heistchance_lvl INTEGER
                    skill_banksecurity_lvl INTEGER
                )
                """
            )

    @app_commands.command(name="join", description="Joins the voice call that you are in currently.")
    async def join(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Hi {interaction.user.mention}! <:GDBemoji:1264147234983776297>', ephemeral=True)


async def setup(bot):
    await bot.add_cog(Voice(bot))
