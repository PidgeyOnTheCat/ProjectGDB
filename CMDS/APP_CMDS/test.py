import random

import discord
from discord.ext import commands, tasks
from discord import app_commands

from Functions import *
from lists import *
from config import *

import aiosqlite, asyncio, random

import openai
openai.api_key = OPENAI_API_KEY

class test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=0.2, count=100)
    async def printer(self, member):
        await member.send(f"hey baby :hot_face:")
        print("brotha")

    @app_commands.command(name="caca", description="cacacaca.")
    async def caca(self, interaction: discord.Interaction):
        self.printer.start("pidgeycat")

async def setup(bot):
    await bot.add_cog(test(bot))
