import discord, os, asyncio, platform
from discord.ext import commands
from dotenv import load_dotenv
from colorama import Fore as f
from version import botVersion

# Load the environment variables
load_dotenv()

# Load the token from the .env file
TOKEN = os.getenv("TOKEN")

# Clear the console
if platform.system() == "Windows":
    os.system("cls")
else:
    os.system("clear")

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
                    {f.RED}.----------------. {f.GREEN}.----------------. {f.BLUE}.----------------. 
                    {f.RED}| .--------------. {f.GREEN}| .--------------. {f.BLUE}| .--------------. |
                    {f.RED}| |    ______    | {f.GREEN}| |  ________    | {f.BLUE}| |   ______     | |
                    {f.RED}| |  .' ___  |   | {f.GREEN}| | |_   ___ `.  | {f.BLUE}| |  |_   _ \    | |
                    {f.RED}| | / .'   \_|   | {f.GREEN}| |   | |   `. \ | {f.BLUE}| |    | |_) |   | |
                    {f.RED}| | | |    ____  | {f.GREEN}| |   | |    | | | {f.BLUE}| |    |  __'.   | |
                    {f.RED}| | \ `.___]  _| | {f.GREEN}| |  _| |___.' / | {f.BLUE}| |   _| |__) |  | |
                    {f.RED}| |  `._____.'   | {f.GREEN}| | |________.'  | {f.BLUE}| |  |_______/   | |
                    {f.RED}| |              | {f.GREEN}| |              | {f.BLUE}| |              | |
                    {f.RED}| '--------------' {f.GREEN}| '--------------' {f.BLUE}| '--------------' |
                    {f.RED}'----------------' {f.GREEN}'----------------' {f.BLUE}'----------------' {f.LIGHTMAGENTA_EX}
        |  Made by: PidgeyCat | |  Version: {botVersion} | |  Discord: discord.gg/PBvj4AfUzr  |

        {f.RESET}
        """
    )


async def main():
    async with bot:
        await startup()
        await load()
        await bot.start(TOKEN)

asyncio.run(main())
