import discord
from discord.ext import commands
from discord import app_commands


from Functions import Functions
from lists import *

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

        Functions.Log(0, f"[{member.name}] has been given the role {role.name}")

async def setup(bot):
    await bot.add_cog(Ranks(bot))