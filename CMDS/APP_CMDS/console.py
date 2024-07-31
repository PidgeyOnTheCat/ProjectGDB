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

class Console(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("console.py has loaded succesfully")

    @app_commands.command(name="load_cog", description="Loads a cog from a file while the bot is running. (admin command)")
    @commands.has_permissions(administrator=True)
    async def load_cog(self, interaction: discord.Interaction, cog: str):
        await self.bot.load_extension(f'CMDS.APP_CMDS.{cog}')
        await interaction.response.send_message(f'{cog} cog loaded', ephemeral=True)
        print(f"{cog} cog loaded")


async def setup(bot):
    await bot.add_cog(Console(bot))
