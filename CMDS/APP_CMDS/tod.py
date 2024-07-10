import discord
from discord import app_commands

from Functions import *


@app_commands.command(name="truth", description="Returns a truth question.")
async def Truth(interaction: discord.Interaction):
    truth = get_truth()
    Embed = discord.Embed(
        title="Truth",
        description=f"{truth}",
        color=discord.Colour.green())

    # Create a view and buttons
    view = discord.ui.View(timeout=None)
    button_truth = discord.ui.Button(style=discord.ButtonStyle.green, label="Truth")
    button_dare = discord.ui.Button(style=discord.ButtonStyle.red, label="Dare")
    button_wyr = discord.ui.Button(style=discord.ButtonStyle.blurple, label="WYR")

    # Add the buttons to the view
    view.add_item(button_truth)
    view.add_item(button_dare)
    view.add_item(button_wyr)

    async def callback_truth(interaction: discord.Interaction):
        truth = get_truth()
        Embed = discord.Embed(
        title="Truth",
        description=f"{truth}",
        color=discord.Colour.green())
        await interaction.response.send_message(embed=Embed, view=view)

    async def callback_dare(interaction: discord.Interaction):
        dare = get_dare()
        Embed = discord.Embed(
        title="Dare",
        description=f"{dare}",
        color=discord.Colour.red())
        await interaction.response.send_message(embed=Embed, view=view)

    async def callback_wyr(interaction: discord.Interaction):
        wyr = get_wyr()
        Embed = discord.Embed(
        title="Would You Rather",
        description=f"{wyr}",
        color=discord.Colour.blue())
        await interaction.response.send_message(embed=Embed, view=view)

    # Give the buttons a function
    button_truth.callback = callback_truth
    button_dare.callback = callback_dare
    button_wyr.callback = callback_wyr

    # Send the original message with the truth question and the button
    await interaction.response.send_message(embed=Embed, view=view)

@app_commands.command(name="dare", description="Returns a dare question.")
async def Dare(interaction: discord.Interaction):
    dare = get_dare()
    Embed = discord.Embed(
        title="Dare",
        description=f"{dare}",
        color=discord.Colour.red())

    # Create a view and buttons
    view = discord.ui.View(timeout=None)
    button_truth = discord.ui.Button(style=discord.ButtonStyle.green, label="Truth")
    button_dare = discord.ui.Button(style=discord.ButtonStyle.red, label="Dare")
    button_wyr = discord.ui.Button(style=discord.ButtonStyle.blurple, label="WYR")

    # Add the buttons to the view
    view.add_item(button_truth)
    view.add_item(button_dare)
    view.add_item(button_wyr)

    async def callback_truth(interaction: discord.Interaction):
        truth = get_truth()
        Embed = discord.Embed(
        title="Truth",
        description=f"{truth}",
        color=discord.Colour.green())
        await interaction.response.send_message(embed=Embed, view=view)

    async def callback_dare(interaction: discord.Interaction):
        dare = get_dare()
        Embed = discord.Embed(
        title="Dare",
        description=f"{dare}",
        color=discord.Colour.red())
        await interaction.response.send_message(embed=Embed, view=view)

    async def callback_wyr(interaction: discord.Interaction):
        wyr = get_wyr()
        Embed = discord.Embed(
        title="Would You Rather",
        description=f"{wyr}",
        color=discord.Colour.blue())
        await interaction.response.send_message(embed=Embed, view=view)

    # Give the buttons a function
    button_truth.callback = callback_truth
    button_dare.callback = callback_dare
    button_wyr.callback = callback_wyr

    # Send the original message with the truth question and the button
    await interaction.response.send_message(embed=Embed, view=view)

@app_commands.command(name="wyr", description="Returns a would you rather question.")
async def WYR(interaction: discord.Interaction):
    wyr = get_wyr()
    Embed = discord.Embed(
        title="Would You Rather",
        description=f"{wyr}",
        color=discord.Colour.blurple())

    # Create a view and buttons
    view = discord.ui.View(timeout=None)
    button_truth = discord.ui.Button(style=discord.ButtonStyle.green, label="Truth")
    button_dare = discord.ui.Button(style=discord.ButtonStyle.red, label="Dare")
    button_wyr = discord.ui.Button(style=discord.ButtonStyle.blurple, label="WYR")

    # Add the buttons to the view
    view.add_item(button_truth)
    view.add_item(button_dare)
    view.add_item(button_wyr)

    async def callback_truth(interaction: discord.Interaction):
        truth = get_truth()
        Embed = discord.Embed(
        title="Truth",
        description=f"{truth}",
        color=discord.Colour.green())
        await interaction.response.send_message(embed=Embed, view=view)

    async def callback_dare(interaction: discord.Interaction):
        dare = get_dare()
        Embed = discord.Embed(
        title="Dare",
        description=f"{dare}",
        color=discord.Colour.red())
        await interaction.response.send_message(embed=Embed, view=view)

    async def callback_wyr(interaction: discord.Interaction):
        wyr = get_wyr()
        Embed = discord.Embed(
        title="Would You Rather",
        description=f"{wyr}",
        color=discord.Colour.blue())
        await interaction.response.send_message(embed=Embed, view=view)

    # Give the buttons a function
    button_truth.callback = callback_truth
    button_dare.callback = callback_dare
    button_wyr.callback = callback_wyr

    # Send the original message with the truth question and the button
    await interaction.response.send_message(embed=Embed, view=view)

async def setup(bot):
    bot.tree.add_command(Truth)
    bot.tree.add_command(Dare)
    bot.tree.add_command(WYR)
