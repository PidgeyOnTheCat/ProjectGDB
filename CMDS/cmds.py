import discord
from discord.ext import commands

from Functions import *

@commands.command()
async def test(ctx):
    await ctx.send("Works!")

@commands.command()
async def truth(ctx):
    # Put the API output in input variable
    input = Functions.get_truth()

    # Embed that holds all the information
    embed = discord.Embed(title="Truth", description=input, color=discord.Colour.blurple())

    # Send the embed
    await ctx.send(embed=embed)

@commands.command()
async def dare(ctx):
    # Put the API output in input variable
    input = Functions.get_dare()

    # Embed that holds all the information
    embed = discord.Embed(title="Dare", description=input, color=discord.Colour.blurple())

    # Send the embed
    await ctx.send(embed=embed)

@commands.command()
async def wyr(ctx):
    # Put the API output in input variable
    input = Functions.get_wyr()

    # Embed that holds all the information
    embed = discord.Embed(title="Would You Rather", description=input, color=discord.Colour.blurple())

    # Send the embed
    await ctx.send(embed=embed)

@commands.command()
async def ping(ctx):
    await ctx.send("Pong")

async def setup(bot):
    bot.add_command(test)
    bot.add_command(truth)
    bot.add_command(dare)
    bot.add_command(wyr)
    bot.add_command(ping)
    