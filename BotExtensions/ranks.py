import discord
from discord.ext import commands
from discord import app_commands

from BotExtensions.functions import *
from BotVariables.lists import *

class Ranks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_unload(self):
        return await super().cog_unload()
    
    # ---------------------------
    # RANK COMMAND
    # ---------------------------
    async def rankup(self, member, guild):
        if guild.id != 678345797330272257:
            return
        
        alerts_channel = self.bot.get_channel(1384275554718711858)

        userdata = await self.bot.db.get_user(member.id, guild.id)
        level = userdata["level"]

        if level not in rank_roles:
            return

        role = guild.get_role(rank_roles[level])
        if not role:
            return

        if role in member.roles:
            return

        await member.add_roles(role)

        await alerts_channel.send(f"**{member.name}** has been awarded the **{role.name}** role for reaching Level {level}!")

        Functions.Log(0, member.name, f"has been given the role {role.name}")

async def setup(bot):
    await bot.add_cog(Ranks(bot))