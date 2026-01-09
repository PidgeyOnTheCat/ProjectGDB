import discord
from discord import app_commands
from discord.ext import commands

from BotExtensions.functions import *
from BotExtensions.errors import *

# -------------------------
# MAIN CLASS
# -------------------------
class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_unload(self):
        return await super().cog_unload()

    # test slash command
    @app_commands.command(name="error", description="Always throws an error")
    async def error_command(self, interaction: discord.Interaction):
        # if Functions.isOwner(interaction):
        if not Functions.isOwner(interaction):
            raise NotOwnerError()
        
        1 / 0  # crash

async def setup(bot):
    cog = ErrorHandler(bot)
    await bot.add_cog(cog)

    # -------------------------
    # GLOBAL SLASH COMMAND ERROR HANDLER
    # -------------------------
    @bot.tree.error
    async def global_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        # Ignore cooldowns
        if isinstance(error, app_commands.CommandOnCooldown):
            return
        
        # Unwrap the original error if it's a CommandInvokeError
        if isinstance(error, discord.app_commands.CommandInvokeError):
            error = error.original

        # Special log type for our custom exception
        if isinstance(error, NotOwnerError):
            Functions.Log(0, interaction.user.name, f"used '{interaction.command.name}' command but doesnt have owner permission")
        elif isinstance(error, NotAdminError):
            Functions.Log(0, interaction.user.name, f"used '{interaction.command.name}' command but doesnt have admin permission")
        else:
            Functions.Log(2, interaction.user.name, f"error in '{interaction.command.name}': {error}")

        # Notify the user
        if not interaction.response.is_done():
            if isinstance(error, NotOwnerError):
                await interaction.response.send_message("You are not allowed to use this command", ephemeral=True)
            elif isinstance(error, NotAdminError):
                await interaction.response.send_message("You are not allowed to use this command", ephemeral=True)
            else:
                await interaction.response.send_message(f"Something went wrong: {error}", ephemeral=True)
