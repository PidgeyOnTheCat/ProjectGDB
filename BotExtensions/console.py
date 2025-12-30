from typing import Literal

import discord
from discord.ext import commands
from discord import app_commands

from BotExtensions.functions import *
from BotExtensions.errors import *
from BotVariables.lists import *


class Console(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="test", description="Test command")
    async def Test(self, interaction: discord.Interaction): 
        if not Functions.isOwner:
            raise NotOwnerError()

        await interaction.response.send_message("Test", ephemeral=True, delete_after=5) 
        Functions.Log(0, "Test command used") 
        Functions.Log(1, "Test command used") 
        Functions.Log(2, "Test command used") 
        Functions.Log(3, "Test command used") 

    @app_commands.command(name="reload", description="Reloads a cog while the bot is running. (admin command)")
    async def reload(self, interaction: discord.Interaction, cog:Literal['console','economy','moderation','uncathegorized','voice','functions','skills','ranks','leaderboards','errorhandler']):
        if not Functions.isAdmin:
            raise NotAdminError()
    
        await self.bot.reload_extension(name=f"BotExtensions.{cog}")
        await interaction.response.send_message(f'{cog} cog reloaded', ephemeral=True)
        Functions.Log(0, f"[{interaction.user.name}] reloaded {cog} cog")


    @app_commands.command(name="shutdown", description="Shuts down the bot. (admin command)")
    async def shutdown(self, interaction: discord.Interaction):
        if not Functions.isAdmin:
            raise NotAdminError()
        
        await interaction.response.send_message("Shutting down the bot", ephemeral=True)
        Functions.Log(0, "Bot is shutting down")
        await self.bot.close()
        os._exit(0)

    @app_commands.command(name="sql", description="Execute SQL query. (admin command)")
    async def sql(self, interaction: discord.Interaction, query: str):
        # Only allow your Discord ID
        if not Functions.isOwner(interaction):
            raise app_commands.AppCommandError("You are not allowed to use this command!")
        
        # Block dangerous queries
        blocked = ["drop table", "delete from levels", "vacuum"]
        if any(b in query.lower() for b in blocked):
            await interaction.response.send_message("Command blocked for safety 💀", ephemeral=True)
            return

        try:
            # Detect SELECT queries
            if query.strip().lower().startswith("select"):
                rows = await self.bot.db.fetchall(query)
                # Format output nicely (limit length if needed)
                output = "\n".join(
                    ", ".join(f"{k}={row[k]}" for k in row.keys())
                    for row in rows
                )
                await interaction.response.send_message(f"Query returned:\n```{output}```", ephemeral=True)
            else:
                # Non-SELECT queries
                await self.bot.db.execute(query)
                await interaction.response.send_message("Query executed successfully.", ephemeral=True)

            Functions.Log(0, f"[{interaction.user.name}] used SQL Query: {query}")

        except Exception as e:
            await interaction.response.send_message(f"Error executing query: {e}", ephemeral=True)
            Functions.Log(2, f"SQL error by {interaction.user.name}: {e}")

    @app_commands.command(name="userlookup", description="Look up a username by ID. (admin command)")
    async def userlookup(self, interaction: discord.Interaction, id: str = None, member: discord.Member = None):
        if not Functions.isAdmin:
            raise NotAdminError()
        
        if id != None:
            try:
                id = int(id)
            except ValueError:
                await interaction.response.send_message("Invalid user ID.", ephemeral=True)
                return

            try:
                username = await self.bot.fetch_user(id)
            except Exception as e:
                await interaction.response.send_message(f"Error fetching user: {e}", ephemeral=True)
                return
            
            await interaction.response.send_message(f"Username of userid: **{id}** is **{username}**", ephemeral=True)
            Functions.Log(0, f"[{interaction.user.name}] used userlookup {id}")

        elif member != None:
            await interaction.response.send_message(f"user id : **{member.id}** \nguild id : **{interaction.guild.id}**", ephemeral=True)

        else:
            await interaction.response.send_message("No id or user given", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Console(bot))
