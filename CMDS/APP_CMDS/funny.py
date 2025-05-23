import requests, random

import discord
from discord import app_commands

from Functions import *

@app_commands.command(name="funny", description="Send a funny meme.")
async def funny(interaction: discord.Interaction):
    #meme_url = get_funny()
    await interaction.response.send_message("https://i.pinimg.com/736x/61/10/99/6110992c09e040f45ee0fd15c88bb91e.jpg")
    Log(0, "Funny command used")

async def setup(bot):
    bot.tree.add_command(funny)