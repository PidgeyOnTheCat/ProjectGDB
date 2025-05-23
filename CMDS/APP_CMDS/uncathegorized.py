import random

import discord
from discord.ext import commands
from discord import app_commands

from Functions import *
from lists import *
from version import botVersion

import aiosqlite, asyncio, random

from groq import Groq

from dotenv import load_dotenv
import os

# Load the environment variables
load_dotenv()
# Load the token from the .env file
AI_API_KEY = os.getenv("AI_API_KEY")
BOTDATA_FILE_PATH = os.getenv("BOTDATA_FILE_PATH")

class Uncathegorized(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("uncathegorized.py has loaded succesfully")

        # level database stuff
        setattr(self.bot, "db", await aiosqlite.connect(f'{BOTDATA_FILE_PATH}/stats.db'))
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

    @app_commands.command(name="hello", description="Says hi and mentions the user.")
    async def Hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Hi {interaction.user.mention}! <:GDBemoji:1264147234983776297>', ephemeral=True)
        Log(0, "Hello command used")

    @app_commands.command(name="ping", description="Responds with Pong.")
    async def Ping(self, interaction: discord.Interaction):
        await interaction.response.send_message('Pong!', ephemeral=True)
        Log(0, "Ping command used")

    @app_commands.command(name="version", description="Responds with the bot version.")
    async def Version(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Bot Version: {botVersion}', ephemeral=True)
        Log(0, "Version command used")

    @app_commands.command(name="say", description="Says what you want it to say.")
    async def Say(self, interaction: discord.Interaction, message: str):
        await interaction.response.send_message(message)
        Log(0, "Say command used")

    @app_commands.command(name="roll", description="Rolls a number from 1 to 6")
    async def Roll(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'{random.randint(1,6)}')
        Log(0, "Roll command used")

    @app_commands.command(name="kys", description="Send a death threat to someone :D")
    async def KYS(self, interaction: discord.Interaction, user: discord.Member, message: str = ""):
        threat = random.choice(threats)
        if message == "":
            await interaction.response.send_message(f'{user.mention}' + threat + '\n:regional_indicator_f::regional_indicator_r::fire:')
        else:
            await interaction.response.send_message(f'{user.mention}' + threat + f'\n{message}' + '\n:regional_indicator_f::regional_indicator_r::fire:')

        Log(0, "KYS command used")

    @app_commands.command(name="leak", description="Leak somebody's IP address for fun (not their actual IP)")
    async def Leak(self, interaction: discord.Interaction, user: discord.Member):
        ip_address = ".".join(str(random.randint(0, 255)) for _ in range(4))
        await interaction.response.send_message(content=f'{ip_address}\n{user.mention}, is this you?')

        Log(0, "Leak command used")

    @app_commands.command(name="test", description="Test command")
    @commands.has_permissions(administrator=True)
    async def Test(self, interaction: discord.Interaction):

        await interaction.response.send_message("Test")

        Log(0, "Test command used")
        Log(1, "Test command used")
        Log(2, "Test command used")
        Log(3, "Test command used")

    @app_commands.command(name="roast", description="Roast someone. ( Why? )")
    async def Roast(self, interaction: discord.Interaction, user: discord.Member, mention: bool=True):
        insult = get_insult()
        if mention:
            await interaction.response.send_message(f"{user.mention}" + f", {insult}")
        else:
            await interaction.response.send_message(f"{user}" + f", {insult}")

        Log(0, "Roast command used")

    @app_commands.command(name="nword", description="Shows how many times a user has said the N-Word.")
    async def nword(self, interaction: discord.Interaction, member: discord.Member = None):
        ctx = await self.bot.get_context(interaction)
        if member == None:
            member = ctx.author

        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT nword FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            nword = await cursor.fetchone()

            if not nword:
                await cursor.execute("INSERT INTO levels (level, xp, money, bank, user, guild, nword, skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl, skill_banksecurity_lvl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (0, 0, 0, 0, member.id, ctx.guild.id, 0, 0, 0, 0, 0, 0))
                await self.bot.commit()

            try:
                nword = nword[0]
            except TypeError:
                nword = 0
            
            await ctx.send(f"{member.mention} has said the N-word **{nword}** times")
            await self.bot.db.commit()

            Log(0, "NWord command used")

    @app_commands.command(name="coinflip", description="Flip a coin.")
    async def Coinflip(self, interaction: discord.Interaction):
        if random.randint(1, 2) == 1:
            await interaction.response.send_message("Heads")
        else:
            await interaction.response.send_message("Tails")

        Log(0, "Coinflip command used")

    @app_commands.command(name="socials", description="Sends PidgeyCat's socials because he's cool.")
    async def Socials(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Sub to PidegyCat here : https://www.youtube.com/@pidgeycat\nFollow my PidgeyCat's Insta here : https://www.instagram.com/pidgeycatalt\nListen to PidgeyCat's spotify playlist here (he loves jack harlow) : https://open.spotify.com/playlist/7DXCaWLuYiPpOc8sBnEhM8?si=5b9f944a15be4932")

        Log(0, "Socials command used")

    @app_commands.command(name="csfinder", description="Finds and checks the Counter-Strike 2 account you are looking for.")
    async def csfinder(self, interaction: discord.Interaction, steamid: str):
        steamid64 = convert_url(steamid)
        if steamid64:
            faceit_url = f'https://faceitfinder.com/profile/{steamid64}'
            leetify_url = f'https://leetify.com/app/profile/{steamid64}'

            await interaction.response.send_message(f"SteamID64: `{steamid64}`\n[Faceit Profile]({faceit_url})\n[Leetify Profile]({leetify_url})")

            Log(0, "CSFinder command used")
        else:
            await interaction.response.send_message("Failed to resolve SteamID64.", ephemeral=True)

            Log(2, "CSFinder Failed to resolve SteamID64")

    @app_commands.command(name="choose", description="Choses one of 2 things.")
    async def choose(self, interaction: discord.Interaction, thing1: str, thing2: str):
        if random.randint(1, 2) == 1:
            await interaction.response.send_message(f"I choose {thing1}.")
        else:
            await interaction.response.send_message(f"I choose {thing2}.")

        Log(0, "Choose command used")

    @app_commands.command(name="ai", description="Prompt AI.")
    async def ai(self, interaction: discord.Interaction, prompt: str):
        # await interaction.response.defer()  # In case response takes a moment

        client = Groq(api_key=AI_API_KEY)
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Your name is GDB. You are a discord bot. You are very funny and you like to joke around. You love dark humor. You are also very helpful and you like to help people. You write short answers."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",
            )
            response = chat_completion.choices[0].message.content
            # print(f"user {interaction.user.name} prompted AI.")
            await interaction.response.send_message(f"**{interaction.user.name} prompted:** *{prompt}*\n{response}")

            Log(0, f"AI command used by {interaction.user.name} with prompt: {prompt}")

        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)
            Log(2, f"AI command failed with error: {str(e)}")

async def setup(bot):
    await bot.add_cog(Uncathegorized(bot))
