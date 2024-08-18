import random
from typing import Literal

import discord
from discord.ext import commands
from discord import app_commands

from Functions import *
from lists import *
from config import *

import aiosqlite, asyncio, random

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("voice.py has loaded succesfully")

    @app_commands.command(name="join", description="Joins the voice call that you are in currently.")
    async def join(self, interaction: discord.Interaction):
        # Get the user who invoked the command and vc
        user = interaction.user

        # Check if the user is in a voice channel
        if user.voice is None or user.voice.channel is None:
            await interaction.response.send_message("You are not in a voice channel.", ephemeral=True)
            return

        voice_channel = user.voice.channel

        if interaction.guild.voice_client is not None:
            await interaction.guild.voice_client.move_to(voice_channel, timeout=1)
        else:
            await voice_channel.connect(reconnect=True, timeout=1)
        
        # Send a response to indicate the bot has joined
        await interaction.response.send_message(f"Joined {voice_channel.name}", ephemeral=True)

    @app_commands.command(name="disconnect", description="Leaves the voice call.")
    async def disconnect(self, interaction: discord.Interaction):

        # Get the bot's voice client
        voice_client = interaction.guild.voice_client

        # Check if the bot is in a voice channel
        if voice_client is None or not voice_client.is_connected():
            await interaction.response.send_message("I am not in a voice channel.", ephemeral=True)
            return

        # Disconnect from the voice channel
        await voice_client.disconnect()

        # Send a response to indicate the bot has left
        await interaction.response.send_message("Left the voice channel.", ephemeral=True)

    @app_commands.command(name="soundboard", description="Play a soundboard sound")
    async def soundboard(self, interaction: discord.Interaction, sound: Literal['kys.wav', 'pipe.mp3', 'hilarious.wav', 'angry.mp3']):
        voice_client = interaction.guild.voice_client

        if voice_client is None or not voice_client.is_connected():
            await interaction.response.send_message("I need to be in a voice channel to play audio.", ephemeral=True)
            return

        audio_path = f'Media/Audio/{sound}'

        try:
            voice_client.stop()
            voice_client.play(discord.FFmpegOpusAudio(audio_path), after=lambda e: print(f"Error: {e}") if e else None)
            await interaction.response.send_message(f"Playing `{sound}`.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Voice(bot))
