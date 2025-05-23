import random
from typing import Literal

import discord
from discord.ext import commands
from discord import app_commands

from Functions import *
from lists import *

import aiosqlite, asyncio, random

class Console(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("console.py has loaded succesfully")

    @app_commands.command(name="reload", description="Reloads a cog while the bot is running. (admin command)")
    @commands.has_permissions(administrator=True)
    async def reload(self, interaction: discord.Interaction, cog:Literal['console','economy','moderation','test','uncathegorized','voice']):
        await self.bot.reload_extension(name=f"CMDS.APP_CMDS.{cog}")
        await interaction.response.send_message(f'{cog} cog reloaded', ephemeral=True)
        Log(0, f"{cog} cog reloaded")

async def setup(bot):
    await bot.add_cog(Console(bot))
