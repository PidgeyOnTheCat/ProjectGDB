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

class Skills(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_unload(self):
        return await super().cog_unload()

    @app_commands.command(name="skills", description="Shows your skilltree.")
    async def skills(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        member = interaction.user
        guild = interaction.guild
        row = await self.bot.db.get_user(member.id, guild.id)

        skillpoints = row["skillpoints"]
        skill_robfull_lvl = row["skill_robfull_lvl"]
        skill_robchance_lvl = row["skill_robchance_lvl"]
        skill_heistchance_lvl = row["skill_heistchance_lvl"]
        skill_banksecurity_lvl = row["skill_banksecurity_lvl"]

        MAX_LVL = 5
        BOTTOM_PADDING = 30

        # ----------------------------
        # Helpers
        # ----------------------------
        def upgrade_cost(lvl: int):
            return None if lvl >= MAX_LVL else lvl + 1

        def cost_text(lvl: int):
            cost = upgrade_cost(lvl)
            return "MAX" if cost is None else f"Cost {cost}"

        def robbing_level():
            return skill_robfull_lvl + skill_robchance_lvl + skill_heistchance_lvl

        font_title = Font.poppins(size=42, variant="bold")
        font_text = Font.poppins(size=28)
        font_text_bold = Font.poppins(size=28, variant="bold")
        font_small = Font.poppins(size=24)
        font_small_bold = Font.poppins(size=24, variant="bold")

        # ----------------------------
        # IMAGE RENDERERS
        # ----------------------------
        def render_main():
            base_height = 360
            height = base_height + BOTTOM_PADDING

            img = Editor(Canvas((720, height)))
            img.rectangle((0, 0), 720, height, "#0e0e0e")

            img.text((360, 40), "Skill Tree", font=font_title, color="white", align="center")
            img.text((360, 95), f"Skillpoints: {skillpoints}", font=font_text, color="#a855f7", align="center")

            img.rectangle((60, 160), 600, 80, "#1a1a1a", radius=20)
            img.text((90, 188), "R - Robbing", font=font_text, color="white")
            img.text((520, 188), f"LVL {robbing_level()}", font=font_text_bold, color="#ef4444")

            img.rectangle((60, 260), 600, 80, "#1a1a1a", radius=20)
            img.text((90, 288), "S - Security", font=font_text, color="white")
            img.text((520, 288), f"LVL {skill_banksecurity_lvl}", font=font_text_bold, color="#22c55e")

            return img

        def render_robbing():
            skills = [
                ("1. Full Rob Chance", skill_robfull_lvl),
                ("2. Rob Chance", skill_robchance_lvl),
                ("3. Heist Chance", skill_heistchance_lvl),
            ]

            CONTENT_TOP = 150
            ROW_HEIGHT = 100
            height = CONTENT_TOP + len(skills) * ROW_HEIGHT + BOTTOM_PADDING

            img = Editor(Canvas((720, height)))
            img.rectangle((0, 0), 720, height, "#0e0e0e")

            img.text((360, 40), "Robbing Skills", font=font_title, color="white", align="center")
            img.text((360, 95), f"Skillpoints: {skillpoints}", font=font_text, color="#a855f7", align="center")

            y = CONTENT_TOP
            for name, lvl in skills:
                img.rectangle((60, y), 600, 80, "#1a1a1a", radius=20)
                img.text((90, y + 28), f"{name} | LVL {lvl}", font=font_small, color="white")
                img.text((500, y + 28), cost_text(lvl), font=font_small_bold, color="#ef4444")
                y += ROW_HEIGHT

            return img

        def render_security():
            base_height = 260
            height = base_height + BOTTOM_PADDING

            img = Editor(Canvas((720, height)))
            img.rectangle((0, 0), 720, height, "#0e0e0e")

            img.text((360, 40), "Security Skills", font=font_title, color="white", align="center")
            img.text((360, 95), f"Skillpoints: {skillpoints}", font=font_text, color="#a855f7", align="center")

            img.rectangle((60, 160), 600, 80, "#1a1a1a", radius=20)
            img.text((90, 188), f"1. Bank Security | LVL {skill_banksecurity_lvl}", font=font_small, color="white")
            img.text((500, 188), cost_text(skill_banksecurity_lvl), font=font_small_bold, color="#22c55e")

            return img

        # ----------------------------
        # Views & Buttons
        # ----------------------------
        view_main = discord.ui.View(timeout=None)
        view_rob = discord.ui.View(timeout=None)
        view_sec = discord.ui.View(timeout=None)

        btn_robbing = discord.ui.Button(label="R", style=discord.ButtonStyle.red)
        btn_security = discord.ui.Button(label="S", style=discord.ButtonStyle.green)
        btn_back = discord.ui.Button(label="Back", style=discord.ButtonStyle.gray)

        btn_r1 = discord.ui.Button(label="1", style=discord.ButtonStyle.red)
        btn_r2 = discord.ui.Button(label="2", style=discord.ButtonStyle.red)
        btn_r3 = discord.ui.Button(label="3", style=discord.ButtonStyle.red)
        btn_s1 = discord.ui.Button(label="1", style=discord.ButtonStyle.green)

        view_main.add_item(btn_robbing)
        view_main.add_item(btn_security)

        view_rob.add_item(btn_r1)
        view_rob.add_item(btn_r2)
        view_rob.add_item(btn_r3)
        view_rob.add_item(btn_back)

        view_sec.add_item(btn_s1)
        view_sec.add_item(btn_back)

        # ----------------------------
        # Navigation
        # ----------------------------
        async def show_main(i):
            file = discord.File(render_main().image_bytes, "skills.png")
            await i.response.edit_message(attachments=[file], view=view_main)

        async def show_rob(i):
            file = discord.File(render_robbing().image_bytes, "skills.png")
            await i.response.edit_message(attachments=[file], view=view_rob)

        async def show_sec(i):
            file = discord.File(render_security().image_bytes, "skills.png")
            await i.response.edit_message(attachments=[file], view=view_sec)

        btn_robbing.callback = show_rob
        btn_security.callback = show_sec
        btn_back.callback = show_main

        # ----------------------------
        # Upgrade logic
        # ----------------------------
        async def upgrade_robbing(stat: str, i):
            nonlocal skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl

            levels = {
                "full": skill_robfull_lvl,
                "chance": skill_robchance_lvl,
                "heist": skill_heistchance_lvl,
            }

            lvl = levels[stat]

            if lvl >= MAX_LVL:
                return await i.response.send_message("Already maxed.", ephemeral=True)

            cost = upgrade_cost(lvl)
            if skillpoints < cost:
                return await i.response.send_message("Not enough skillpoints.", ephemeral=True)

            skillpoints -= cost
            if stat == "full":
                skill_robfull_lvl += 1
            elif stat == "chance":
                skill_robchance_lvl += 1
            else:
                skill_heistchance_lvl += 1

            await self.bot.db.execute(
                """
                UPDATE levels
                SET skillpoints=?, skill_robfull_lvl=?, skill_robchance_lvl=?, skill_heistchance_lvl=?
                WHERE user=? AND guild=?
                """,
                (skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl, member.id, guild.id)
            )

            await show_rob(i)

        async def upgrade_security(i):
            nonlocal skillpoints, skill_banksecurity_lvl

            if skill_banksecurity_lvl >= MAX_LVL:
                return await i.response.send_message("Already maxed.", ephemeral=True)

            cost = upgrade_cost(skill_banksecurity_lvl)
            if skillpoints < cost:
                return await i.response.send_message("Not enough skillpoints.", ephemeral=True)

            skillpoints -= cost
            skill_banksecurity_lvl += 1

            await self.bot.db.execute(
                """
                UPDATE levels
                SET skillpoints=?, skill_banksecurity_lvl=?
                WHERE user=? AND guild=?
                """,
                (skillpoints, skill_banksecurity_lvl, member.id, guild.id)
            )

            await show_sec(i)

        btn_r1.callback = lambda i: upgrade_robbing("full", i)
        btn_r2.callback = lambda i: upgrade_robbing("chance", i)
        btn_r3.callback = lambda i: upgrade_robbing("heist", i)
        btn_s1.callback = upgrade_security

        # ----------------------------
        # Initial send
        # ----------------------------
        file = discord.File(render_main().image_bytes, "skills.png")
        await interaction.followup.send(file=file, view=view_main, ephemeral=True)
        Functions.Log(0, interaction.user.name, f"used the skills command")


async def setup(bot):
    await bot.add_cog(Skills(bot))
