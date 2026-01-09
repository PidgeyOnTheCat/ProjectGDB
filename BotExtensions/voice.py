import random
from typing import Literal

import discord
from discord.ext import commands
from discord import app_commands

from BotExtensions.functions import *
from BotVariables.lists import *

import aiosqlite, asyncio, random
from pathlib import Path

from dotenv import load_dotenv
import os

# Load the environment variables
load_dotenv()
# Load the token from the .env file
BOTDATA_FILE_PATH = os.getenv("BOTDATA_FILE_PATH")

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="join", description="Joins the voice call that you are in currently.")
    async def join(self, interaction: discord.Interaction):
        user = interaction.user

        # Check if the user is in a voice channel
        if user.voice is None or user.voice.channel is None:
            await interaction.response.send_message("You are not in a voice channel.", ephemeral=True)
            return

        voice_channel = user.voice.channel
        
        try:
            if interaction.guild.voice_client is not None:
                # Bot is already in a voice channel
                await interaction.guild.voice_client.move_to(voice_channel, timeout=10.0)
            else:
                # Bot is not in any voice channel
                await voice_channel.connect(timeout=10.0, reconnect=True)
                
            await interaction.response.send_message(f"Joined {voice_channel.name}", ephemeral=True)

            Functions.Log(0, interaction.user.name, f"joined bot in vc {voice_channel.name}")
            
        except asyncio.TimeoutError:
            await interaction.response.send_message("Connection timed out. Please try again.", ephemeral=True)
            Functions.Log(1, None, "connection timed out.")
        except discord.ClientException as e:
            await interaction.response.send_message(f"Failed to join voice channel: {str(e)}", ephemeral=True)
            Functions.Log(2, None, f"failed to join voice channel: {str(e)}")
        except Exception as e:
            await interaction.response.send_message(f"An unexpected error occurred: {str(e)}", ephemeral=True)
            Functions.Log(2, None, f"an unexpected error occurred: {str(e)}")

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

        Functions.Log(0, interaction.user.name, "left the voice channel.")

    @app_commands.command(name="soundboard", description="Play a soundboard sound")
    @app_commands.describe(sound="The sound to play")
    async def soundboard(self, interaction: discord.Interaction, sound: str):
        # Get the current list of sounds
        sounds_list = []
        audio_dir = Path(BOTDATA_FILE_PATH) / "Media/Audio"
        for sound_file in audio_dir.iterdir():
            if sound_file.suffix in (".wav", ".mp3"):
                sounds_list.append(sound_file.name)
        
        # Validate the input
        if sound not in sounds_list:
            await interaction.response.send_message(
                "Invalid sound choice. Use the autocomplete to select a valid sound.",
                ephemeral=True
            )
            return

        voice_client = interaction.guild.voice_client

        if voice_client is None or not voice_client.is_connected():
            await interaction.response.send_message("I need to be in a voice channel to play audio.", ephemeral=True)
            return

        audio_path = f'{BOTDATA_FILE_PATH}/Media/Audio/{sound}'

        try:
            voice_client.stop()
            voice_client.play(discord.FFmpegOpusAudio(audio_path), after=lambda e: print(f"Error: {e}") if e else None)
            await interaction.response.send_message(f"Playing `{sound}`.", ephemeral=True)
            Functions.Log(0, interaction.user.name, f"playing {sound}.")
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)
            Functions.Log(2, interaction.user.name, f"an error occurred: {str(e)}")

    @soundboard.autocomplete("sound")
    async def soundboard_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> list[app_commands.Choice[str]]:
        audio_dir = Path(BOTDATA_FILE_PATH) / "Media/Audio"
        
        # Make a list of just the filenames (as strings)
        sounds_list = [f.name for f in audio_dir.iterdir() if f.suffix in (".wav", ".mp3")]
        
        # Filter based on user input
        filtered_sounds = [
            app_commands.Choice(name=sound, value=sound)
            for sound in sounds_list
            if current.lower() in sound.lower()
        ][:25]  # Discord limits to 25 choices

        return filtered_sounds

async def setup(bot):
    await bot.add_cog(Voice(bot))
