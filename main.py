import discord
from discord.ext import commands

import asyncio

from config import *
from lists import *

bot = commands.Bot(command_prefix=">", intents=discord.Intents.all())

@bot.event
async def on_ready():
    synced = await bot.tree.sync()

    print('---------------------------------')
    print(f'Successfully synced {len(synced)} commands.')
    print(f'Succesfully logged in as {bot.user}\n_________________________________')

async def load():
    # Importing all of the cogs
    await bot.load_extension('CMDS.APP_CMDS.economy')
    await bot.load_extension('CMDS.APP_CMDS.uncathegorized')

    # Load all the bot commands
    await bot.load_extension('CMDS.APP_CMDS.tod')
    await bot.load_extension('CMDS.APP_CMDS.funny')
    await bot.load_extension('CMDS.cmds')

    # Unused bot commands
    # await bot.load_extension('CMDS.APP_CMDS.moderation')

async def main():
    async with bot:
        await load()
        await bot.start(TOKEN)

asyncio.run(main())
