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


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Start the voice call XP giver
        self.f = self.bot.get_cog("Functions")

    async def cog_unload(self):
        self.f.update_xp.cancel()
        return await super().cog_unload()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages sent by bots
        if message.author.bot:
            return
        else:
            author = message.author
            guild = message.guild

        # Respond to every message
        # await message.channel.send(f"Works! You said: {message.content}")

        # Give user XP and money
        await self.f.give_xp(author, guild, 0)

        # Fetch user data

        data = await self.bot.db.get_user(author.id, guild.id)
        nword = data['nword']

        # -------------------------
        # N-WORD FILTER
        # -------------------------
        # Convert message content to lowercase
        message_content = message.content.lower()

        # Assuming nword_list is a list of words like ["nword", "otherbadword"]
        nword_set = set(word.lower() for word in nword_list)

        # Split message into words to avoid substring issues
        words_in_message = message_content.split()
        count = sum(word in nword_set for word in words_in_message)

        if count > 0:
            # Fetch current nword count from DB (or set to 0 if not found)
            row = await self.bot.db.fetchone(
                "SELECT nword FROM levels WHERE user = ? AND guild = ?",
                (author.id, guild.id)
            )
            nword = row[0] if row else 0
            nword += count

            # Update DB
            await self.bot.db.execute(
                "UPDATE levels SET nword = ? WHERE user = ? AND guild = ?",
                (nword, author.id, guild.id)
            )

            # Send warning and log
            await message.channel.send(":thumbsdown: \nNo racism!")
            Functions.Log(0, f"[{author.name}] said the N-word {count} time(s).")

        # -------------------------
        # One-in-a-million Easter Egg
        # -------------------------
        if random.randint(1, 1000000) == 1:
            await message.channel.send(
                f"{author.mention} has discovered a one in a million easter egg and gained 5 extra levels!"
            )
            await self.f.levelup(author, guild)
            await self.f.levelup(author, guild)
            await self.f.levelup(author, guild)
            await self.f.levelup(author, guild)
            await self.f.levelup(author, guild)

            Functions.Log(0, f"{author.name} discovered a one-in-a-million easter egg and gained 5 extra levels!")

        # Important: let commands still work
        await self.bot.process_commands(message)

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction: discord.Interaction, command: app_commands.Command):
        # Give XP for slash commands
        await self.f.give_xp(interaction.user, interaction.guild, 1)

    # Define all of the app commands
    @app_commands.command(name="levelup", description="Level up by paying money.")
    async def levelup(self, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction)
        member = ctx.author

        # Fetch userdata
        userdata = await self.bot.db.get_user(member.id, ctx.guild.id)
        level = userdata['level']
        money = userdata['money']
        xp = userdata['xp']

        xp_required = (level + 1) * 100
        money_required = xp_required - xp

        # Make it cost 5 times more money to level up past lvl 100
        if level <= 100:
            money_required *= 10
        else:
            money_required *= 50

        if money >= money_required:
            await self.f.levelup(member, ctx.guild)

            money -= money_required
            await self.bot.db.execute(
                "UPDATE levels SET money = ? WHERE user = ? AND guild = ?",
                (money, member.id, ctx.guild.id)
            )
            await ctx.send(f"You have leveled up to level {level + 1} by paying {money_required} <:gdb_emoji_coin:1376156520030404650>!", ephemeral=True)
            Functions.Log(0, f"[{member.name}] leveled up by paying {money_required}")

        else:
            await ctx.send(f"You don't have enough <:gdb_emoji_coin:1376156520030404650> for a levelup\nYou need {money_required} <:gdb_emoji_coin:1376156520030404650> but you only have {money} <:gdb_emoji_coin:1376156520030404650>", ephemeral=True)

    @app_commands.command(name="deposit",description="Deposit a certain amount of money into your bank account.")
    async def deposit(self, interaction: discord.Interaction,amount: Literal['100', '500', '1000', '5000', '10000', '50000', '100000', 'all']):
        ctx = await self.bot.get_context(interaction)
        member = ctx.author
        guild = ctx.guild

        # Fetch user row (guarantees it exists)
        row = await self.bot.db.get_user(member.id, guild.id)

        money = row['money']
        bank = row['bank']

        # Determine deposit amount
        if amount == 'all':
            deposited = money
        else:
            deposited = int(amount)

        # Check for invalid deposits
        if money <= 0 or deposited <= 0:
            await ctx.send(f"You can't deposit nothing into your bank account",ephemeral=True)
            return

        # Cap deposit to available money
        if deposited > money:
            deposited = money

        # Update balances
        money -= deposited
        bank += deposited

        # Persist changes
        await self.bot.db.execute(
            "UPDATE levels SET money = ?, bank = ? WHERE user = ? AND guild = ?",
            (money, bank, member.id, guild.id)
        )

        # Feedback message
        await ctx.send(
            f"{member.mention} has deposited {deposited} <:gdb_emoji_coin:1376156520030404650> into their bank account."
        )

        Functions.Log(0, f"[{member.name}] deposited {deposited} coins")


    @app_commands.command(name="withdraw", description="Withdraw a certain amount of money from your bank account.")
    async def withdraw(self,interaction: discord.Interaction,amount: Literal['100', '500', '1000', '5000', '10000', '50000', '100000', 'all']):
        ctx = await self.bot.get_context(interaction)
        member = ctx.author
        guild = ctx.guild

        # Fetch user row (guarantees it exists)
        row = await self.bot.db.get_user(member.id, guild.id)

        money = row['money']
        bank = row['bank']

        # Determine withdraw amount
        if amount == 'all':
            withdrawn = bank
        else:
            withdrawn = int(amount)

        # Check for invalid withdraw
        if bank <= 0 or withdrawn <= 0:
            await ctx.send(f"You can't withdraw nothing from your bank account.",ephemeral=True)
            return

        # Cap withdrawal to available bank balance
        if withdrawn > bank:
            withdrawn = bank

        # Update balances
        money += withdrawn
        bank -= withdrawn

        # Persist changes
        await self.bot.db.execute("UPDATE levels SET money = ?, bank = ? WHERE user = ? AND guild = ?",(money, bank, member.id, guild.id))

        # Feedback message
        await ctx.send(f"{member.name} has withdrawn {withdrawn} <:gdb_emoji_coin:1376156520030404650> from their bank account.")

        Functions.Log(0, f"[{member.mention}] Withdraw command used")

    @app_commands.command(name="addmoney", description="Give a user a certain amount of money. (admin command)")
    async def addmoney(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        ctx = await self.bot.get_context(interaction)
        guild = ctx.guild

        if interaction.user.guild_permissions.administrator:
            row = await self.bot.db.get_user(member.id, guild.id)

            money = row['money']
            bank = row['bank']

            if amount <= 0:
                await interaction.response.send_message("You can't give the specified amount to the person. Amount can only be a positive number.", ephemeral=True)
            else:
                money += amount
                await self.bot.db.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (money, member.id, ctx.guild.id))
                await interaction.response.send_message(f"**{member}** now has **{money}** money and {bank} money in their bank.", ephemeral=True)

                Functions.Log(0, f"[{member.name}] Add money command used (admin)")
        else:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

    @app_commands.command(name="removemoney", description="Take a certain amount of money from a user. (admin command)")
    async def removemoney(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        ctx = await self.bot.get_context(interaction)
        guild = ctx.guild

        if interaction.user.guild_permissions.administrator:
            row = await self.bot.db.get_user(member.id, guild.id)

            money = row['money']
            bank = row['bank']

            if amount <= 0:
                await interaction.response.send_message("You can't take the specified amount to the person. Amount can only be a positive number.", ephemeral=True)
            else:
                if money >= amount:
                    money -= amount
                else:
                    bank_take = amount - money
                    money = 0

                    if bank >= bank_take:
                        bank -= bank_take
                    else:
                        bank = 0
                    
                await self.bot.db.execute("UPDATE levels SET money = ?, bank = ? WHERE user = ? AND guild = ?", (money, bank, member.id, guild.id))
                
                await interaction.response.send_message(f"**{member}** now has **{money}** money and {bank} money in their bank.", ephemeral=True)

                Functions.Log(0, f"[{member.name}] Remove money command used (admin)")
        else:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

    @app_commands.command(name="stats", description="Show a user's current statistics")
    async def stats(self, interaction: discord.Interaction, member: discord.Member = None):
        try:
            ctx = await self.bot.get_context(interaction)
            if member is None:
                member = ctx.author
            guild = ctx.guild

            # Ensure the user row exists (insert if not exists)
            row = await self.bot.db.get_user(member.id, guild.id)
            xp = row['xp']
            level = row['level']
            money = row['money']
            bank = row['bank']
            skillpoints = row['skillpoints']

            # Calculate XP left for next level
            xp_required = (level + 1) * 100
            xp_left = xp_required - xp

            user_data = {
                "name": member.name,
                "level": level,
                "xp": xp,
                "xp_left": xp_left,
                "money": money,
                "bank": bank,
                "skillpoints": skillpoints
            }

            # Build the stats card image
            background = Editor(Canvas((900, 330), color="#141414"))
            profile_picture = await load_image_async(str(member.avatar.url))
            profile = Editor(profile_picture).resize((150, 150)).circle_image()
            font1 = Font.poppins(size=40)
            font2 = Font.poppins(size=30)
            coin_icon = Image.open(rf"{BOTDATA_FILE_PATH}/Media/Images/gdb_emoji_coin_downscaled.png").resize((96, 96))

            card_right_shape = [(650, 0), (800, 330), (900, 330), (900, 0)]
            background.polygon(card_right_shape, color="#CFCFCF")
            background.paste(profile, (30, 30))

            background.rectangle((30, 260), width=650, height=40, color="#FFFFFF", radius=22)
            background.bar((30, 260), max_width=650, height=41,
                        percentage=user_data["xp"] / (user_data["xp"] + user_data["xp_left"]) * 100,
                        color="#9323CB", radius=22)

            background.text((200, 40), user_data["name"], font=font1, color="#FFFFFF")
            background.rectangle((200, 100), width=350, height=2, fill="#7D1DAD")
            background.text(
                (200, 130),
                f"Level: {user_data['level']} | XP: {user_data['xp']} / {user_data['xp'] + user_data['xp_left']}",
                font=font2,
                color="#FFFFFF"
            )
            background.text(
                (200, 170),
                f"Money: {user_data['money']} | Bank: {user_data['bank']}",
                font=font2,
                color="#FFFFFF"
            )
            background.text(
                (200, 210),
                f"Skillpoints: {user_data['skillpoints']}",
                font=font2,
                color="#FFFFFF"
            )

            background.paste(coin_icon, (900-96-20, 20))

            file = discord.File(fp=background.image_bytes, filename="stats_card.png")
            await interaction.response.send_message(file=file)

            Functions.Log(0, f"[{ctx.author.name}] used stats command")

        except Exception as e:
            Functions.Log(2, f"Error in stats command: {e}")
            await interaction.response.send_message(f"An error occurred while fetching stats: {e}", ephemeral=True)

    @app_commands.command(name="pickpocket", description="Rob a user for their money.")
    @app_commands.checks.cooldown(1, Functions.hoursToSeconds(3), key=lambda i: (i.guild_id, i.user.id))
    async def pickpocket(self, interaction: discord.Interaction, member: discord.Member):
        ctx = await self.bot.get_context(interaction)
        robber = ctx.author

        if member == ctx.author:
            await interaction.response.send_message("You can't rob yourself.", ephemeral=True)
        else:
            rowRobber = await self.bot.db.get_user(robber.id, ctx.guild.id)
            rowVictim = await self.bot.db.get_user(member.id, ctx.guild.id)
            
            moneyrobber = rowRobber['money']
            bankrobber = rowRobber['bank']

            skill_robchance_lvl = rowRobber['skill_robchance_lvl']
            skill_robfull_lvl = rowRobber['skill_robfull_lvl']

            moneymember = rowVictim['money']
            bankmember = rowVictim['bank']


            if moneymember >= 500:
                baseChance = 20 # 20% chance to rob
                baseChance += skill_robchance_lvl * 3
                chance = random.randint(1, 100)

                if chance <= baseChance:
                    chance = random.randint(1, 100)
                    baseChanceFullrob = 10
                    baseChanceFullrob += skill_robfull_lvl * 2
                    if chance <= baseChanceFullrob:
                        robtake = moneymember

                        moneymember -= robtake
                        moneyrobber += robtake

                        await interaction.response.send_message(f"{robber.mention} stole all <:gdb_emoji_coin:1376156520030404650> from {member.mention}!")
                    else:
                        robtake = moneymember * random.uniform(0.40, 0.75)
                        robtake = int(round(robtake, 0))

                        moneymember -= robtake
                        moneyrobber += robtake

                        await interaction.response.send_message(f"{robber.mention} stole {robtake} <:gdb_emoji_coin:1376156520030404650> from {member.mention}!")

                else:
                    fine = moneymember * random.uniform(0.5, 0.75)
                    fine = int(round(fine, 0))

                    if moneyrobber < fine: # robber doesnt have enough money
                        fine -= moneyrobber
                        moneyrobber = 0

                        if bankrobber < fine: # robber doesnt have enough bank
                            fine = int(round(fine / 2, 0))
                            bankrobber -= fine
                            bankmember += fine
                        else: # robber does have enough bank to pay
                            bankrobber -= fine
                    else: # robber does have enough money to pay
                        moneyrobber -= fine
                        bankmember += fine

                    await interaction.response.send_message(f"{robber.mention} just got caught trying to pickpocket {member.mention} and got fined for {fine} <:gdb_emoji_coin:1376156520030404650>.")
                    
                    await self.bot.db.execute("UPDATE levels SET money = ?, bank = ? WHERE user = ? AND guild = ?", (moneyrobber, bankrobber, robber.id, ctx.guild.id))
                    await self.bot.db.execute("UPDATE levels SET money = ?, bank = ? WHERE user = ? AND guild = ?", (moneymember, bankmember, member.id, ctx.guild.id))

                    Functions.Log(0, f"[{robber.name}] used pickpocket on {member.name}")

            else:
                await interaction.response.send_message("This user doesn't have enough money in their pocket. \n(500 <:gdb_emoji_coin:1376156520030404650> required)", ephemeral=True)
    
    @pickpocket.error
    async def on_pickpocket_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"Please wait {Functions.timeConvert(error.retry_after)}", ephemeral=True)

    @app_commands.command(name="heist", description="Rob a user for their bank money.")
    @app_commands.checks.cooldown(1, Functions.hoursToSeconds(12), key=lambda i: (i.guild_id, i.user.id)) # 24 hour cooldown
    async def heist(self, interaction: discord.Interaction, member: discord.Member):
        ctx = await self.bot.get_context(interaction)
        robber = ctx.author

        if member == ctx.author:
            await interaction.response.send_message("You can't rob yourself.", ephemeral=True)
        else:
            robberdata = await self.bot.db.get_user(robber.id, ctx.guild.id)
            memberdata = await self.bot.db.get_user(member.id, ctx.guild.id)

            bankrobber = robberdata['bank']
            skill_heistchance_lvl = robberdata['skill_heistchance_lvl']

            bankmember = memberdata['bank']

            if bankmember >= 25000:
                baseChance = 10 # 10% chance
                baseChance += skill_heistchance_lvl * 1
                chance = random.randint(1, 100)
                if chance <= baseChance: # successful heist
                    take = bankmember * random.uniform(0.8, 1.0)
                    take = int(round(take, 0))

                    bankrobber += take
                    bankmember -= take

                    await interaction.response.send_message(f"{robber.mention} stole {take} <:gdb_emoji_coin:1376156520030404650> from {member.mention}!")

                else: # failed heist
                    fine = bankmember * random.uniform(0.75, 0.90)
                    fine = int(round(fine, 0))

                    if bankrobber < fine:
                        fine = int(round(fine / 2, 0))

                        bankrobber -= fine
                        bankmember += fine
                    else:
                        bankrobber -= fine
                        bankmember += fine

                    await interaction.response.send_message(f"{robber.mention} just got caught trying to rob {member.mention} and got fined for {fine} <:gdb_emoji_coin:1376156520030404650>.")

                await self.bot.db.execute("UPDATE levels SET bank = ? WHERE user = ? AND guild = ?", (bankrobber, robber.id, ctx.guild.id))
                await self.bot.db.execute("UPDATE levels SET bank = ? WHERE user = ? AND guild = ?", (bankmember, member.id, ctx.guild.id))

                Functions.Log(0, f"[{robber.name}] used heist on {member.name}")

            else:
                await interaction.response.send_message("This user doesn't have enough money in their bank. \n(25000 <:gdb_emoji_coin:1376156520030404650> required)", ephemeral=True)

    @heist.error
    async def on_heist_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"Please wait {Functions.timeConvert(error.retry_after)}", ephemeral=True)
                
    @app_commands.command(name="work", description="Work to get money.")
    @app_commands.checks.cooldown(1, Functions.hoursToSeconds(8), key=lambda i: (i.guild_id, i.user.id))
    async def work(self, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction)
        member = ctx.author

        userdata = await self.bot.db.get_user(member.id, ctx.guild.id)

        money = userdata['money']    

        paycheck = random.randint(300, 900)
        money += paycheck

        await interaction.response.send_message(f"{member.mention} went to work and has gained {paycheck} <:gdb_emoji_coin:1376156520030404650>.")

        await self.bot.db.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (money, member.id, ctx.guild.id))
        Functions.Log(0, f"[{member.name}] used Work command")

    @work.error
    async def on_work_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"Please wait {Functions.timeConvert(error.retry_after)}", ephemeral=True)

    @app_commands.command(name="daily", description="Get your daily money bonus.")
    @app_commands.checks.cooldown(1, Functions.hoursToSeconds(24), key=lambda i: (i.guild_id, i.user.id))
    async def daily(self, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction)
        member = ctx.author

        userdata = await self.bot.db.get_user(member.id, ctx.guild.id)

        money = userdata['money']

        dailyreward = round(random.randint(1500, 2500), -2)
        money += dailyreward

        await interaction.response.send_message(f"{member.mention} has gained {dailyreward} <:gdb_emoji_coin:1376156520030404650> from their daily reward.")

        await self.bot.db.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (money, member.id, ctx.guild.id))
        Functions.Log(0, f"[{member.name}] used Daily command")

    @daily.error
    async def on_daily_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"Please wait {Functions.timeConvert(error.retry_after)}", ephemeral=True)

    @app_commands.command(name="sendmoney", description="Give a user a certain amount of money.")
    @app_commands.describe(amount="How much money to send (positive number or 'all')")
    async def sendmoney(self, interaction: discord.Interaction, member: discord.Member, amount: str):
        ctx = await self.bot.get_context(interaction)
        sender = ctx.author

        if member == sender:
            await interaction.response.send_message(f"You can't send {amount} money to yourself.", ephemeral=True)
        else:
            senderdata = await self.bot.db.get_user(sender.id, ctx.guild.id)
            memberdata = await self.bot.db.get_user(member.id, ctx.guild.id)

            moneysender = senderdata['money']
            moneymember = memberdata['money']

            if amount.lower() == 'all':
                amount = moneysender
            else:
                try:
                    amount = int(amount)
                except ValueError:
                    await interaction.response.send_message("The amount must be a positive number or 'all'.", ephemeral=True)
                    return

            if amount <= 0:
                await interaction.response.send_message("You can't give the specified amount to the person. Amount can only be a positive number.", ephemeral=True)
            else:
                if moneysender < amount:
                    await interaction.response.send_message(f"You can't send {amount} <:gdb_emoji_coin:1376156520030404650> because you don't have enough.", ephemeral=True)
                else:
                    moneysender -= amount
                    moneymember += amount

                    await interaction.response.send_message(f"{sender.mention} sent {amount} <:gdb_emoji_coin:1376156520030404650> to {member.mention}.")

                    await self.bot.db.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (moneysender, sender.id, ctx.guild.id))
                    await self.bot.db.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (moneymember, member.id, ctx.guild.id))

                    Functions.Log(0, f"[{sender.name}] sent {amount} to {member.name}")


    @app_commands.command(name="bet", description="Bet on a number ranging from 1 to 3.")
    async def bet(self, interaction: discord.Interaction, amount: int, bet: int):
        ctx = await self.bot.get_context(interaction)
        member = ctx.author

        userdata = await self.bot.db.get_user(member.id, ctx.guild.id)

        money = userdata['money']

        if amount > money:
            await interaction.response.send_message(f"You can't bet {amount} <:gdb_emoji_coin:1376156520030404650> because you dont have enough.", ephemeral=True)
        else:
            rng = random.randint(1, 3)
            if bet == rng:
                money += amount
                await interaction.response.send_message(f"{member.mention} bet {amount} <:gdb_emoji_coin:1376156520030404650> on {bet} and won.")
            else:
                money -= amount
                await interaction.response.send_message(f"{member.mention} bet {amount} <:gdb_emoji_coin:1376156520030404650> on {bet} and lost. The number was {rng}")

            await self.bot.db.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (money, member.id, ctx.guild.id))

            Functions.Log(0, f"[{member.name}] used Bet command")

    @app_commands.command(name="skills", description="Shows your skilltree.")
    async def skills(self, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction)
        member = ctx.author
        guild = ctx.guild

        row = await self.bot.db.get_user(member.id, guild.id)

        skillpoints = row["skillpoints"]
        skill_robfull_lvl = row["skill_robfull_lvl"]
        skill_robchance_lvl = row["skill_robchance_lvl"]
        skill_heistchance_lvl = row["skill_heistchance_lvl"]
        skill_banksecurity_lvl = row["skill_banksecurity_lvl"]

        MAX_LVL = 5

        def robbing_level():
            return skill_robfull_lvl + skill_robchance_lvl + skill_heistchance_lvl

        def upgrade_cost(lvl: int):
            return None if lvl >= MAX_LVL else lvl + 1

        def cost_text(lvl: int):
            cost = upgrade_cost(lvl)
            return "MAX" if cost is None else f"Cost `{cost}`"

        def refresh_embeds():
            embedMain.description = (
                f"Skillpoints : `{skillpoints}`\n\n"
                f"**R**obbing : `{robbing_level()}`\n"
                f"**S**ecurity : `{skill_banksecurity_lvl}`"
            )

            embedRobbing.description = (
                f"Skillpoints : `{skillpoints}`\n"
                f"Level : `{robbing_level()}`\n\n"
                f"1. Full Rob Chance LVL : `{skill_robfull_lvl}` ({cost_text(skill_robfull_lvl)})\n"
                f"2. Rob Chance LVL : `{skill_robchance_lvl}` ({cost_text(skill_robchance_lvl)})\n"
                f"3. Heist Chance LVL : `{skill_heistchance_lvl}` ({cost_text(skill_heistchance_lvl)})"
            )

            embedSecurity.description = (
                f"Skillpoints : `{skillpoints}`\n"
                f"Level : `{skill_banksecurity_lvl}`\n\n"
                f"1. Bank Security LVL : `{skill_banksecurity_lvl}` ({cost_text(skill_banksecurity_lvl)})"
            )

        embedMain = discord.Embed(title="Skill Category Tree", color=discord.Color.blurple())
        embedRobbing = discord.Embed(title="Robbing Skill Tree", color=discord.Color.red())
        embedSecurity = discord.Embed(title="Security Skill Tree", color=discord.Color.green())
        refresh_embeds()

        viewMain = discord.ui.View(timeout=None)
        viewRobbing = discord.ui.View(timeout=None)
        viewSecurity = discord.ui.View(timeout=None)

        btn_robbing = discord.ui.Button(label="R", style=discord.ButtonStyle.red)
        btn_security = discord.ui.Button(label="S", style=discord.ButtonStyle.green)
        btn_back = discord.ui.Button(label="Back", style=discord.ButtonStyle.gray)

        btn_r1 = discord.ui.Button(label="1", style=discord.ButtonStyle.red)
        btn_r2 = discord.ui.Button(label="2", style=discord.ButtonStyle.red)
        btn_r3 = discord.ui.Button(label="3", style=discord.ButtonStyle.red)
        btn_s1 = discord.ui.Button(label="1", style=discord.ButtonStyle.green)

        viewMain.add_item(btn_robbing)
        viewMain.add_item(btn_security)

        viewRobbing.add_item(btn_r1)
        viewRobbing.add_item(btn_r2)
        viewRobbing.add_item(btn_r3)
        viewRobbing.add_item(btn_back)

        viewSecurity.add_item(btn_s1)
        viewSecurity.add_item(btn_back)

        async def go_robbing(i):
            Functions.Log(0, f"[{member.name}] opened Robbing skill tree")
            await i.response.edit_message(embed=embedRobbing, view=viewRobbing)

        async def go_security(i):
            Functions.Log(0, f"[{member.name}] opened Security skill tree")
            await i.response.edit_message(embed=embedSecurity, view=viewSecurity)

        async def go_back(i):
            Functions.Log(0, f"[{member.name}] returned to main skill tree")
            await i.response.edit_message(embed=embedMain, view=viewMain)

        btn_robbing.callback = go_robbing
        btn_security.callback = go_security
        btn_back.callback = go_back

        async def upgrade_robbing(stat: str, i):
            nonlocal skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl

            if stat == "full":
                lvl = skill_robfull_lvl
            elif stat == "chance":
                lvl = skill_robchance_lvl
            else:
                lvl = skill_heistchance_lvl

            if lvl >= MAX_LVL:
                return await i.response.send_message("This skill is already maxed.", ephemeral=True)

            cost = upgrade_cost(lvl)
            if skillpoints < cost:
                return await i.response.send_message(
                    f"You need `{cost}` skillpoints.", ephemeral=True
                )

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
                SET skillpoints = ?, skill_robfull_lvl = ?, skill_robchance_lvl = ?, skill_heistchance_lvl = ?
                WHERE user = ? AND guild = ?
                """,
                (
                    skillpoints,
                    skill_robfull_lvl,
                    skill_robchance_lvl,
                    skill_heistchance_lvl,
                    member.id,
                    guild.id,
                )
            )

            refresh_embeds()
            Functions.Log(0, f"[{member.name}] upgraded robbing skill ({stat}) | cost {cost}")
            await i.response.edit_message(embed=embedRobbing, view=viewRobbing)

        async def upgrade_security(i):
            nonlocal skillpoints, skill_banksecurity_lvl

            if skill_banksecurity_lvl >= MAX_LVL:
                return await i.response.send_message("This skill is already maxed.", ephemeral=True)

            cost = upgrade_cost(skill_banksecurity_lvl)
            if skillpoints < cost:
                return await i.response.send_message(
                    f"You need `{cost}` skillpoints.", ephemeral=True
                )

            skillpoints -= cost
            skill_banksecurity_lvl += 1

            await self.bot.db.execute(
                """
                UPDATE levels
                SET skillpoints = ?, skill_banksecurity_lvl = ?
                WHERE user = ? AND guild = ?
                """,
                (skillpoints, skill_banksecurity_lvl, member.id, guild.id)
            )

            refresh_embeds()
            Functions.Log(0, f"[{member.name}] upgraded Bank Security | cost {cost}")
            await i.response.edit_message(embed=embedSecurity, view=viewSecurity)

        btn_r1.callback = lambda i: upgrade_robbing("full", i)
        btn_r2.callback = lambda i: upgrade_robbing("chance", i)
        btn_r3.callback = lambda i: upgrade_robbing("heist", i)
        btn_s1.callback = upgrade_security

        Functions.Log(0, f"[{member.name}] opened Skills menu")
        await interaction.response.send_message(embed=embedMain, view=viewMain, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Economy(bot))
