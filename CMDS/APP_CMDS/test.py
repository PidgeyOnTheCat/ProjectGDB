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
        self.index = 0
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=5.0)
    async def printer(self):
        print(self.index)
        self.index += 1

async def setup(bot):
    await bot.add_cog(test(bot))
