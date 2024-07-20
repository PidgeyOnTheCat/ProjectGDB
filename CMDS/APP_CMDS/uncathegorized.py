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

class Uncathegorized(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("uncathegorized.py has loaded succesfully")

        # level database stuff
        setattr(self.bot, "db", await aiosqlite.connect("BotData\stats.db"))
        await asyncio.sleep(3)
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS levels (level INTEGER, xp INTEGER, money INTEGER, bank INTEGER, user INTEGER, guild INTEGER, nword INTEGER, skillpoints INTEGER, skill_robfull_lvl INTEGER, skill_robchance_lvl INTEGER, skill_heistchance_lvl INTEGER)")

    @app_commands.command(name="hello", description="Says hi and mentions the user.")
    async def Hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Hi {interaction.user.mention}! <:GDBemoji:1264147234983776297>', ephemeral=True)

    @app_commands.command(name="ping", description="Responds with Pong.")
    async def Ping(self, interaction: discord.Interaction):
        await interaction.response.send_message('Pong!', ephemeral=True)

    @app_commands.command(name="say", description="Says what you want it to say.")
    async def Say(self, interaction: discord.Interaction, thing: str):
        await interaction.response.send_message(thing)

    @app_commands.command(name="roll", description="Rolls a number from 1 to 6")
    async def Roll(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'{random.randint(1,6)}')

    @app_commands.command(name="kys", description="Send a death threat to someone :D")
    async def KYS(self, interaction: discord.Interaction, user: discord.Member, message: str = ""):
        threat = random.choice(threats)
        if message == "":
            await interaction.response.send_message(f'{user.mention}' + threat + '\n:regional_indicator_f::regional_indicator_r::fire:')
        else:
            await interaction.response.send_message(f'{user.mention}' + threat + f'\n{message}' + '\n:regional_indicator_f::regional_indicator_r::fire:')

    @app_commands.command(name="leak", description="Leak somebody's IP address for fun (not their actual IP)")
    async def Leak(self, interaction: discord.Interaction, user: discord.Member):
        ip_address = ".".join(str(random.randint(0, 255)) for _ in range(4))
        await interaction.response.send_message(content=f'{ip_address}\n{user.mention}, is this you?')

    @app_commands.command(name="test", description="Test command")
    async def Test(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Test")
        else:
            await interaction.response.send_message("You need the administrator permission to use this command.", ephemeral=True)

    @app_commands.command(name="alerts", description="Turn message alerts on or off")
    async def Alerts(self, interaction: discord.Interaction, choice: bool):
        global Send_Alerts  # Declare Send_Alerts as global to modify the global variable

        if interaction.user.guild_permissions.administrator:
            Send_Alerts = choice  # Update the global Send_Alerts variable
            with open('config.py', 'r') as config_file:
                config_lines = config_file.readlines()

            for i, line in enumerate(config_lines):
                if line.startswith("Send_Alerts"):
                    config_lines[i] = f'Send_Alerts = {choice}\n'
                    break

            with open('config.py', 'w') as config_file:
                config_file.writelines(config_lines)

            if choice:
                await interaction.response.send_message("Message alerts are now **on**", ephemeral=True)
            else:
                await interaction.response.send_message("Message alerts are now **off**", ephemeral=True)
        else:
            await interaction.response.send_message("You need the administrator permission to use this command.", ephemeral=True)

    @app_commands.command(name="roast", description="Roast someone. ( Why? )")
    async def Roast(self, interaction: discord.Interaction, user: discord.Member, mention: bool=True):
        insult = get_insult()
        if mention:
            await interaction.response.send_message(f"{user.mention}" + f", {insult}")
        else:
            await interaction.response.send_message(f"{user}" + f", {insult}")

    @app_commands.command(name="nword", description="Shows how many times a user has said the N-Word.")
    async def nword(self, interaction: discord.Interaction, member: discord.Member = None):
        ctx = await self.bot.get_context(interaction)
        if member == None:
            member = ctx.author

        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT nword FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            nword = await cursor.fetchone()

            if not nword:
                await cursor.execute("INSERT INTO levels (level, xp, money, bank, user, guild, nword, skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)", (0, 0, 0, 0, member.id, ctx.guild.id, 0, 0, 0, 0, 0))
                await self.bot.commit()

            try:
                nword = nword[0]
            except TypeError:
                nword = 0
            
            await ctx.send(f"{member.mention} has said the N-word **{nword}** times")
            await self.bot.db.commit()

    @app_commands.command(name="coinflip", description="Flip a coin.")
    async def Coinflip(self, interaction: discord.Interaction):
        if random.randint(1, 2) == 1:
            await interaction.response.send_message("Heads")
        else:
            await interaction.response.send_message("Tails")

    @app_commands.command(name="socials", description="Sends PidgeyCat's socials because he's cool.")
    async def Socials(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Sub to PidegyCat here : https://www.youtube.com/@pidgeycat\nFollow my PidgeyCat's Insta here : https://www.instagram.com/pidgeycatalt\nListen to PidgeyCat's spotify playlist here (he loves jack harlow) : https://open.spotify.com/playlist/7DXCaWLuYiPpOc8sBnEhM8?si=5b9f944a15be4932")

    @app_commands.command(name="csfinder", description="Finds and checks the Counter-Strike 2 account you are looking for.")
    async def csfinder(self, interaction: discord.Interaction, steamid: str):
        steamid64 = convert_url(steamid)
        if steamid64:
            faceit_url = f'https://faceitfinder.com/profile/{steamid64}'
            leetify_url = f'https://leetify.com/app/profile/{steamid64}'

            await interaction.response.send_message(f"SteamID64: `{steamid64}`\n[Faceit Profile]({faceit_url})\n[Leetify Profile]({leetify_url})")
        else:
            await interaction.response.send_message("Failed to resolve SteamID64.", ephemeral=True)

    @app_commands.command(name="choose", description="Choses one of 2 things.")
    async def choose(self, interaction: discord.Interaction, thing1: str, thing2: str):
        if random.randint(1, 2) == 1:
            await interaction.response.send_message(f"I choose {thing1}.")
        else:
            await interaction.response.send_message(f"I choose {thing2}.")

    @app_commands.command(name="chatgpt", description="Gives ChatGPT a prompt.")
    async def chatgpt(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.defer()  # Defer the response to indicate processing

        try:
            # Make a request to the OpenAI API
            response = openai.Completion.create(
                model="gpt-3.5-turbo",  # You can use the appropriate model here
                prompt=prompt,
                max_tokens=150
            )

            # Extract the text from the response
            result = response.choices[0].text.strip()

            # Send the result back to the user
            await interaction.followup.send(result)
        except Exception as e:
            # Handle exceptions (e.g., API errors)
            await interaction.followup.send(f"An error occurred: {str(e)}")

async def setup(bot):
    await bot.add_cog(Uncathegorized(bot))
