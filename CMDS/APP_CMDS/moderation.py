import datetime

import discord
from discord import app_commands

class Moderation(app_commands.Group):
    @app_commands.command(name="timeout", description="Timeout someone in the server")
    async def Timeout(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        time: float = 1.0,
        reason: str = "None"
        ):

        embed = discord.Embed(
            title="Timeout",
            description=f"{user.mention} has been timed out for {time} minutes\nReason: {reason}"
        )

        if interaction.user.guild_permissions.administrator:
            await user.timeout(datetime.timedelta(minutes=time), reason=reason)  # Pass until as a positional argument
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("You need the administrator permission to use this command.", ephemeral=True)

async def setup(bot):
    bot.tree.add_command(Moderation(name="moderation", description="Use admin commands on users"))