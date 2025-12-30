import discord
from discord.ext import commands
from discord import app_commands

from BotExtensions.functions import *
from BotVariables.lists import *
from BotVariables.version import botVersion

import random, os
from pathlib import Path

from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
AI_API_KEY = os.getenv("AI_API_KEY")
BOTDATA_FILE_PATH = os.getenv("BOTDATA_FILE_PATH")

class Uncathegorized(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -------------------- BASIC COMMANDS -------------------- #
    @app_commands.command(name="hello", description="Says hi and mentions the user.")
    async def Hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Hi {interaction.user.mention}! <:gdb_emoji_logo:1264147234983776297>', ephemeral=True)
        Functions.Log(0, interaction.user.name, f"used Hello command")

    @app_commands.command(name="ping", description="Responds with Pong.")
    async def Ping(self, interaction: discord.Interaction):
        await interaction.response.send_message('Pong!', ephemeral=True)
        Functions.Log(0, interaction.user.name, f"used Ping command")

    @app_commands.command(name="version", description="Responds with the bot version.")
    async def Version(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Bot Version: {botVersion}', ephemeral=True)
        Functions.Log(0, interaction.user.name, f"used Version command")

    @app_commands.command(name="say", description="Says what you want it to say.")
    async def Say(self, interaction: discord.Interaction, message: str):
        await interaction.response.send_message(message)
        Functions.Log(0, interaction.user.name, f"used Say command with message: {message}")

    @app_commands.command(name="roll", description="Rolls a number from 1 to 6")
    async def Roll(self, interaction: discord.Interaction):
        roll_result = random.randint(1, 6)
        await interaction.response.send_message(f'{roll_result}')
        Functions.Log(0, interaction.user.name, f"used Roll command: {roll_result}")

    # -------------------- FUN COMMANDS -------------------- #
    @app_commands.command(name="kys", description="Send a death threat to someone :D")
    async def KYS(self, interaction: discord.Interaction, user: discord.Member, message: str = ""):
        threat = random.choice(threats)
        content = f"{user.mention} {threat}"
        if message:
            content += f"\n{message}"
        content += "\n:regional_indicator_f::regional_indicator_r::fire:"
        await interaction.response.send_message(content)
        Functions.Log(0, interaction.user.name, f"used KYS command on {user.name}")

    @app_commands.command(name="leak", description="Leak somebody's IP address for fun (not real)")
    async def Leak(self, interaction: discord.Interaction, user: discord.Member):
        ip_address = ".".join(str(random.randint(0, 255)) for _ in range(4))
        await interaction.response.send_message(content=f'{ip_address}\n{user.mention}, is this you?')
        Functions.Log(0, interaction.user.name, f"used Leak command on {user.name}")

    @app_commands.command(name="funny", description="Send a funny meme.")
    async def Funny(self, interaction: discord.Interaction):
        await interaction.response.send_message("https://i.pinimg.com/736x/61/10/99/6110992c09e040f45ee0fd15c88bb91e.jpg")
        Functions.Log(0, interaction.user.name, f"used Funny command")

    @app_commands.command(name="coinflip", description="Flip a coin.")
    async def Coinflip(self, interaction: discord.Interaction):
        result = "Heads" if random.randint(1, 2) == 1 else "Tails"
        await interaction.response.send_message(result)
        Functions.Log(0, interaction.user.name, f"used Coinflip command: {result}")

    @app_commands.command(name="choose", description="Chooses one of 2 things.")
    async def Choose(self, interaction: discord.Interaction, thing1: str, thing2: str):
        choice = thing1 if random.randint(1, 2) == 1 else thing2
        await interaction.response.send_message(f"I choose {choice}.")
        Functions.Log(0, interaction.user.name, f"used Choose command: {choice}")

    # -------------------- SOCIAL COMMANDS -------------------- #
    @app_commands.command(name="socials", description="Sends PidgeyCat's socials.")
    async def Socials(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Sub to PidgeyCat here: https://www.youtube.com/@pidgeycat\n"
            "Follow on Instagram: https://www.instagram.com/pidgeycat\n"
            "Listen to Spotify playlist: https://open.spotify.com/playlist/7DXCaWLuYiPpOc8sBnEhM8?si=5b9f944a15be4932"
        )
        Functions.Log(0, interaction.user.name, f"used Socials command")

    @app_commands.command(name="csfinder", description="Finds a Counter-Strike 2 account.")
    async def CSFinder(self, interaction: discord.Interaction, steamid: str):
        steamid64 = Functions.convert_url(steamid)
        if steamid64:
            faceit_url = f'https://faceitfinder.com/profile/{steamid64}'
            leetify_url = f'https://leetify.com/app/profile/{steamid64}'
            await interaction.response.send_message(f"SteamID64: `{steamid64}`\n[Faceit Profile]({faceit_url})\n[Leetify Profile]({leetify_url})")
            Functions.Log(0, interaction.user.name, f"used CSFinder command: {steamid64}")
        else:
            await interaction.response.send_message("Failed to resolve SteamID64.", ephemeral=True)
            Functions.Log(2, interaction.user.name, f"CSFinder failed to resolve SteamID64: {steamid}")

    @app_commands.command(name="nword", description="Shows how many times a user has said the N-Word.")
    async def nword(self, interaction: discord.Interaction, member: discord.Member = None):
        ctx = await self.bot.get_context(interaction)
        if member is None:
            member = ctx.author

        userdata = await self.bot.db.get_user(member.id, ctx.guild.id)

        await interaction.response.send_message(f"{member.mention} has said the N-word **{userdata['nword']}** times")

        Functions.Log(0, interaction.user.name, f"checked N-word count: {userdata['nword']}")

    # -------------------- TRUTH/DARE/WYR -------------------- #
    async def _send_tdw(self, interaction: discord.Interaction, type_: str):
        """Internal function to send Truth/Dare/WYR with buttons"""
        if type_ == "truth":
            content = Functions.get_truth()
            color = discord.Colour.green()
        elif type_ == "dare":
            content = Functions.get_dare()
            color = discord.Colour.red()
        else:
            content = Functions.get_wyr()
            color = discord.Colour.blurple()

        embed = discord.Embed(title=type_.capitalize(), description=content, color=color)
        view = discord.ui.View(timeout=None)

        button_truth = discord.ui.Button(style=discord.ButtonStyle.green, label="Truth")
        button_dare = discord.ui.Button(style=discord.ButtonStyle.red, label="Dare")
        button_wyr = discord.ui.Button(style=discord.ButtonStyle.blurple, label="WYR")
        view.add_item(button_truth)
        view.add_item(button_dare)
        view.add_item(button_wyr)

        async def callback(inter: discord.Interaction, new_type: str):
            await self._send_tdw(inter, new_type)
            Functions.Log(0, interaction.user.name, f"clicked {new_type.capitalize()} button")

        button_truth.callback = lambda i: callback(i, "truth")
        button_dare.callback = lambda i: callback(i, "dare")
        button_wyr.callback = lambda i: callback(i, "wyr")

        await interaction.response.send_message(embed=embed, view=view)
        Functions.Log(0, interaction.user.name, f"used {type_.capitalize()} command")

    @app_commands.command(name="truth", description="Returns a truth question.")
    async def Truth(self, interaction: discord.Interaction):
        await self._send_tdw(interaction, "truth")

    @app_commands.command(name="dare", description="Returns a dare question.")
    async def Dare(self, interaction: discord.Interaction):
        await self._send_tdw(interaction, "dare")

    @app_commands.command(name="wyr", description="Returns a would you rather question.")
    async def WYR(self, interaction: discord.Interaction):
        await self._send_tdw(interaction, "wyr")

    # -------------------- ROAST -------------------- #
    @app_commands.command(name="roast", description="Roast someone.")
    async def Roast(self, interaction: discord.Interaction, user: discord.Member, mention: bool = True):
        insult = Functions.get_insult()
        target = user.mention if mention else user.name
        await interaction.response.send_message(f"{target}, {insult}")
        Functions.Log(0, interaction.user.name, f"used Roast command on {user.name}")

    # -------------------- AI COMMAND -------------------- #
    @app_commands.command(name="ai", description="Prompt AI.")
    async def AI(self, interaction: discord.Interaction, prompt: str):
        client = Groq(api_key=AI_API_KEY)
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Your name is GDB. You are a discord bot. You are funny and helpful."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
            )
            response = chat_completion.choices[0].message.content
            await interaction.response.send_message(f"**{interaction.user.name} prompted:** *{prompt}*\n{response}")
            Functions.Log(0, interaction.user.name, f"used AI command with prompt: {prompt}")
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)
            Functions.Log(2, interaction.user.name, f"AI command failed: {str(e)}")


async def setup(bot):
    await bot.add_cog(Uncathegorized(bot))
