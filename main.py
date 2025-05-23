import discord
from discord.ext import commands

from dotenv import load_dotenv
import os

from version import botVersion

import asyncio

# Load the environment variables
load_dotenv()

# Load the token from the .env file
TOKEN = os.getenv("TOKEN")

try:
    os.system('cls')
except:
    os.system('clear')

bot = commands.Bot(command_prefix=">", intents=discord.Intents.all())

@bot.event
async def on_ready():
    synced = await bot.tree.sync()

    print('---------------------------------')
    print(f'successfully synced {len(synced)} commands.')
    print(f'successfully logged in as {bot.user}\nBot version: {botVersion}\n_________________________________')

async def load():
    # Importing all of the cogs
    await bot.load_extension('CMDS.APP_CMDS.economy')
    await bot.load_extension('CMDS.APP_CMDS.uncathegorized')
    await bot.load_extension('CMDS.APP_CMDS.voice')
    await bot.load_extension('CMDS.APP_CMDS.console')

    # Load all the bot commands
    await bot.load_extension('CMDS.APP_CMDS.tod')
    await bot.load_extension('CMDS.APP_CMDS.funny')
    await bot.load_extension('CMDS.cmds')

    # Unused bot commands
    # await bot.load_extension('CMDS.APP_CMDS.test')
    # await bot.load_extension('CMDS.APP_CMDS.moderation')

async def startup():
    print(
        rf"""
                    .----------------. .----------------. .----------------. 
                    | .--------------. | .--------------. | .--------------. |
                    | |    ______    | | |  ________    | | |   ______     | |
                    | |  .' ___  |   | | | |_   ___ `.  | | |  |_   _ \    | |
                    | | / .'   \_|   | | |   | |   `. \ | | |    | |_) |   | |
                    | | | |    ____  | | |   | |    | | | | |    |  __'.   | |
                    | | \ `.___]  _| | | |  _| |___.' / | | |   _| |__) |  | |
                    | |  `._____.'   | | | |________.'  | | |  |_______/   | |
                    | |              | | |              | | |              | |
                    | '--------------' | '--------------' | '--------------' |
                    '----------------' '----------------' '----------------' 
        |  Made by: PidgeyCat | |  Version: {botVersion} | |  Discord: discord.gg/PBvj4AfUzr  |


        """
    )


async def main():
    async with bot:
        await startup()
        await load()
        await bot.start(TOKEN)

asyncio.run(main())
