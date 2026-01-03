import discord
from discord.ext import commands
from discord import app_commands

import random, os

from typing import Literal
from dotenv import load_dotenv
from easy_pil import *
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

from BotExtensions.functions import *
from BotVariables.lists import *

# Load the environment variables
load_dotenv()
BOTDATA_FILE_PATH = os.getenv("BOTDATA_FILE_PATH")


class Leaderboards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_unload(self):
        return await super().cog_unload()

    @app_commands.command(name="leaderboard", description="Shows the top 10 highest users in certain categories.")
    async def leaderboard(self, interaction: discord.Interaction, type: Literal['levels', 'nword', 'cocksize']):
        if type == 'levels':
            await self.leaderboard_levels(interaction)
        elif type == 'nword':
            await self.leaderboard_nword(interaction)
        elif type == 'cocksize':
            await self.leaderboard_cocksize(interaction)
        
        else:
            interaction.response.send_message("Invalid leaderboard type.", ephemeral=True)

    async def leaderboard_levels(self, interaction):
        await interaction.response.defer()

        guild = interaction.guild

        rows = await self.bot.db.fetchall(
            """
            SELECT user, level
            FROM levels
            WHERE guild = ?
            ORDER BY level DESC
            LIMIT 10
            """,
            (guild.id,)
        )

        width = 820
        height = 140 + (len(rows) * 100)

        bg = Editor(Canvas((width, height), color="#0e0e0e"))

        font_title = Font.poppins(size=46, variant="bold")
        font_name = Font.poppins(size=32)
        font_rank = Font.poppins(size=32, variant="bold")
        font_lvl = Font.poppins(size=30, variant="bold")

        # Title
        bg.text(
            (width // 2, 45),
            "Level Leaderboard",
            font=font_title,
            color="#ffffff",
            align="center"
        )

        # Load medal icon
        trophy_gold = Image.open(rf"{BOTDATA_FILE_PATH}/Media/Images/gdb_trophy_gold.png").resize((80, 80))
        trophy_silver = Image.open(rf"{BOTDATA_FILE_PATH}/Media/Images/gdb_trophy_silver.png").resize((80, 80))
        trophy_bronze = Image.open(rf"{BOTDATA_FILE_PATH}/Media/Images/gdb_trophy_bronze.png").resize((80, 80))
        medal_positions = ["#FFD700", "#C0C0C0", "#CD7F32"]  # gold, silver, bronze

        y = 120
        for i, row in enumerate(rows, start=1):
            user_id = row["user"]
            level = row["level"]
            member = guild.get_member(user_id)
            username = member.name if member else f"User {user_id}"

            # Card background
            bg.rectangle(
                (40, y),
                width=width - 80,
                height=85,
                color="#1a1a1a",
                radius=20
            )

            # Rank color for top 3
            rank_color = medal_positions[i-1] if i <= 3 else "#ffffff"

            # Rank number
            bg.text(
                (65, y + 28),  # slightly lower
                f"#{i}",
                font=font_rank,
                color=rank_color
            )

            # Medal icon for top 3
            if i <= 3:
                bg.paste(Editor(trophy_gold if i == 1 else trophy_silver if i == 2 else trophy_bronze), (117, y + 3))

            # Username (move a bit right if medal)
            x_username = 200 if i <= 3 else 150
            bg.text(
                (x_username, y + 28),  # slightly lower
                username,
                font=font_name,
                color="#ffffff"
            )

            # Level (bold, moved slightly left)
            bg.text(
                (width - 200, y + 28),
                f"LVL {level}",
                font=font_lvl,
                color="#a855f7"
            )

            y += 100

        file = discord.File(fp=bg.image_bytes, filename="leaderboard.png")
        await interaction.followup.send(file=file)

    async def leaderboard_nword(self, interaction):
        await interaction.response.defer()

        guild = interaction.guild

        rows = await self.bot.db.fetchall(
            """
            SELECT user, nword
            FROM levels
            WHERE guild = ?
            ORDER BY nword DESC
            LIMIT 10
            """,
            (guild.id,)
        )

        width = 820
        height = 140 + (len(rows) * 100)

        bg = Editor(Canvas((width, height), color="#0e0e0e"))

        font_title = Font.poppins(size=46, variant="bold")
        font_name = Font.poppins(size=32)
        font_rank = Font.poppins(size=32, variant="bold")
        font_count = Font.poppins(size=30, variant="bold")

        # Title
        bg.text(
            (width // 2, 45),
            "N-Word Leaderboard",
            font=font_title,
            color="#ffffff",
            align="center"
        )

        # Load medal icon
        trophy_gold = Image.open(rf"{BOTDATA_FILE_PATH}/Media/Images/gdb_trophy_gold.png").resize((80, 80))
        trophy_silver = Image.open(rf"{BOTDATA_FILE_PATH}/Media/Images/gdb_trophy_silver.png").resize((80, 80))
        trophy_bronze = Image.open(rf"{BOTDATA_FILE_PATH}/Media/Images/gdb_trophy_bronze.png").resize((80, 80))
        medal_positions = ["#FFD700", "#C0C0C0", "#CD7F32"]  # gold, silver, bronze

        y = 120
        for i, row in enumerate(rows, start=1):
            user_id = row["user"]
            count = row["nword"]
            member = guild.get_member(user_id)
            username = member.name if member else f"User {user_id}"

            # Card background
            bg.rectangle(
                (40, y),
                width=width - 80,
                height=85,
                color="#1a1a1a",
                radius=20
            )

            # Rank color for top 3
            rank_color = medal_positions[i-1] if i <= 3 else "#ffffff"

            # Rank number
            bg.text(
                (65, y + 28),
                f"#{i}",
                font=font_rank,
                color=rank_color
            )

            # Medal icon for top 3
            if i <= 3:
                bg.paste(Editor(trophy_gold if i == 1 else trophy_silver if i == 2 else trophy_bronze), (117, y + 3))

            # Username (move a bit right if medal)
            x_username = 200 if i <= 3 else 150
            bg.text(
                (x_username, y + 28),
                username,
                font=font_name,
                color="#ffffff"
            )

            # Nword count (purple, no label)
            bg.text(
                (width - 200, y + 28),
                str(count),
                font=font_count,
                color="#a855f7"
            )

            y += 100

        file = discord.File(fp=bg.image_bytes, filename="leaderboard.png")
        await interaction.followup.send(file=file)

    async def leaderboard_cocksize(self, interaction):
        await interaction.response.defer()

        guild = interaction.guild

        rows = await self.bot.db.fetchall(
            """
            SELECT user, cocksize
            FROM levels
            WHERE guild = ?
            ORDER BY cocksize DESC
            LIMIT 10
            """,
            (guild.id,)
        )

        width = 820
        height = 140 + (len(rows) * 100)

        bg = Editor(Canvas((width, height), color="#0e0e0e"))

        font_title = Font.poppins(size=46, variant="bold")
        font_name = Font.poppins(size=32)
        font_rank = Font.poppins(size=32, variant="bold")
        font_count = Font.poppins(size=30, variant="bold")

        # Title
        bg.text(
            (width // 2, 45),
            "Cocksize Leaderboard",
            font=font_title,
            color="#ffffff",
            align="center"
        )

        # Load medal icon
        trophy_gold = Image.open(rf"{BOTDATA_FILE_PATH}/Media/Images/gdb_trophy_gold.png").resize((80, 80))
        trophy_silver = Image.open(rf"{BOTDATA_FILE_PATH}/Media/Images/gdb_trophy_silver.png").resize((80, 80))
        trophy_bronze = Image.open(rf"{BOTDATA_FILE_PATH}/Media/Images/gdb_trophy_bronze.png").resize((80, 80))
        medal_positions = ["#FFD700", "#C0C0C0", "#CD7F32"]  # gold, silver, bronze

        y = 120
        for i, row in enumerate(rows, start=1):
            user_id = row["user"]
            count = row["cocksize"]
            member = guild.get_member(user_id)
            username = member.name if member else f"User {user_id}"

            # Card background
            bg.rectangle(
                (40, y),
                width=width - 80,
                height=85,
                color="#1a1a1a",
                radius=20
            )

            # Rank color for top 3
            rank_color = medal_positions[i-1] if i <= 3 else "#ffffff"

            # Rank number
            bg.text(
                (65, y + 28),
                f"#{i}",
                font=font_rank,
                color=rank_color
            )

            # Medal icon for top 3
            if i <= 3:
                bg.paste(Editor(trophy_gold if i == 1 else trophy_silver if i == 2 else trophy_bronze), (117, y + 3))

            # Username (move a bit right if medal)
            x_username = 200 if i <= 3 else 150
            bg.text(
                (x_username, y + 28),
                username,
                font=font_name,
                color="#ffffff"
            )

            # cocksize number (purple, no label)
            bg.text(
                (width - 200, y + 28),
                text=str(count) + "cm",
                font=font_count,
                color="#a855f7"
            )

            y += 100

        file = discord.File(fp=bg.image_bytes, filename="leaderboard.png")
        await interaction.followup.send(file=file)


async def setup(bot):
    await bot.add_cog(Leaderboards(bot))
