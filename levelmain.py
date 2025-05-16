import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import aiosqlite
import random
import asyncio

load_dotenv()

TOKEN = os.getenv("TOKEN")
BOTDATA_FILE_PATH = os.getenv("BOTDATA_FILE_PATH")

bot = commands.Bot(command_prefix=">", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Succesfully logged in as {bot.user}\n_________________________________')

    # level database stuff
    setattr(bot, "db", await aiosqlite.connect(f'{BOTDATA_FILE_PATH}/stats.db'))
    await asyncio.sleep(3)
    async with bot.db.cursor() as cursor:
        await cursor.execute("CREATE TABLE IF NOT EXISTS levels (level INTEGER, xp INTEGER, user INTEGER, guild INTEGER, money INTEGER, bank INTEGER)")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    author = message.author
    guild = message.guild
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT xp FROM levels WHERE user = ? AND guild = ?", (author.id, guild.id))
        xp = await cursor.fetchone()
        await cursor.execute("SELECT level FROM levels WHERE user = ? AND guild = ?", (author.id, guild.id))
        level = await cursor.fetchone()

        if not xp or not level:
            await cursor.execute("INSERT INTO levels (level, xp, user, guild, money, bank) VALUES (?, ?, ?, ?, ?, ?)",(0, 0, author.id, guild.id, 0, 0))
            await bot.db.commit()

        try:
            xp = xp[0]
            level = level[0]
        except TypeError:
            xp = 0
            level = 0

        # Gives the user xp
        xp += random.randint(15, 40)
        await cursor.execute("UPDATE levels SET xp = ? WHERE user = ? AND guild = ?", (xp, author.id, guild.id))
        
        # Calculate xp needed for level up
        xp_required = (level + 1) * 100

        if xp >= xp_required:
            level += 1
            await cursor.execute("UPDATE levels SET level = ? WHERE user = ? AND guild = ?", (level, author.id, guild.id))
            await cursor.execute("UPDATE levels SET xp = ? WHERE user = ? AND guild = ?", (0, author.id, guild.id))
            await message.channel.send(f"{author.mention} has leveled up to level **{level}**!")

        await bot.db.commit()
        await bot.process_commands(message)

@bot.command(aliases=['rank', 'lvl'])
async def level(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT xp FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
        xp = await cursor.fetchone()
        await cursor.execute("SELECT level FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
        level = await cursor.fetchone()

        if not xp or not level:
            await cursor.execute("INSERT INTO levels (level, xp, user, guild) VALUES (?, ?, ?, ?)", (0, 0, member.id, ctx.guild.id))
            await bot.commit()

        try:
            xp = xp[0]
            level = level[0]
        except TypeError:
            xp = 0
            level = 0

        # Calculate xp needed for level up
        xp_required = (level + 1) * 100
        xp_left = xp_required - xp 

        em = discord.Embed(title=f"{member.name}'s Level", description=f"Level : `{level}`\nXP: `{xp}`\nLeft : `{xp_left}`")
        await ctx.send(embed=em)

bot.run(TOKEN)
