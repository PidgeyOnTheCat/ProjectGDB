import discord
from discord.ext import commands, tasks
from discord import app_commands

import aiosqlite, asyncio, random

import config
from config import *
from lists import *

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # stats the voice call xp giver
        self.update_xp.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print("economy.py has loaded succesfully")
        
        # level database stuff
        setattr(self.bot, "db", await aiosqlite.connect("BotData\stats.db"))
        await asyncio.sleep(3)
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS levels (level INTEGER, xp INTEGER, money INTEGER, bank INTEGER, user INTEGER, guild INTEGER, nword INTEGER, skillpoints INTEGER, skill_robfull_lvl INTEGER, skill_robchance_lvl INTEGER, skill_heistchance_lvl INTEGER)")


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        author = message.author
        guild = message.guild
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT xp FROM levels WHERE user = ? AND guild = ?", (author.id, guild.id))
            xp = await cursor.fetchone()
            await cursor.execute("SELECT level FROM levels WHERE user = ? AND guild = ?", (author.id, guild.id))
            level = await cursor.fetchone()
            await cursor.execute("SELECT money FROM levels WHERE user = ? AND guild = ?", (author.id, guild.id))
            money = await cursor.fetchone()
            await cursor.execute("SELECT bank FROM levels WHERE user = ? AND guild = ?", (author.id, guild.id))
            bank = await cursor.fetchone()
            await cursor.execute("SELECT nword FROM levels WHERE user = ? AND guild = ?", (author.id, guild.id))
            nword = await cursor.fetchone()
            await cursor.execute("SELECT skillpoints FROM levels WHERE user = ? AND guild = ?", (author.id, guild.id))
            skillpoints = await cursor.fetchone()

            if not xp or not level:
                await cursor.execute("INSERT INTO levels (level, xp, money, bank, user, guild, nword, skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)", (0, 0, 0, 0, author.id, guild.id, 0, 0, 0, 0, 0))
                await self.bot.db.commit()

            try:
                xp = xp[0]
                level = level[0]
                money = money[0]
                bank = bank[0]
                nword = nword[0]
                skillpoints = skillpoints[0]
            except TypeError:
                xp = 0
                level = 0
                money = 0
                bank = 0
                nword = 0
                skillpoints = 0

            # Gives the user xp and money
            xp += random.randint(15, 40) # 15, 40 / 100, 10000
            money += random.randint(20, 55) # 20, 55 / 1000, 10000
            await cursor.execute("UPDATE levels SET xp = ? WHERE user = ? AND guild = ?", (xp, author.id, guild.id))
            await cursor.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (money, author.id, guild.id))
            
            # Calculate xp needed for level up
            xp_required = (level + 1) * 100

            if xp >= xp_required:
                level += 1

                if level % 5 == 0:
                    #skillpointsamount = level / 5
                    #skillpointsamount = int(skillpointsamount)
                    skillpointsamount = 1
                    skillpoints += skillpointsamount
                    await message.channel.send(f"{author.mention} has leveled up to level **{level}** and has gained **{skillpointsamount}** skill points!")
                else:
                    await message.channel.send(f"{author.mention} has leveled up to level **{level}**!")

                await cursor.execute("UPDATE levels SET level = ? WHERE user = ? AND guild = ?", (level, author.id, guild.id))
                await cursor.execute("UPDATE levels SET xp = ? WHERE user = ? AND guild = ?", (0, author.id, guild.id))
                await cursor.execute("UPDATE levels SET skillpoints = ? WHERE user = ? AND guild = ?", (skillpoints, author.id, guild.id))

            for word in nword_list:
                if word in message.content.lower():
                    nword += 1
                    await cursor.execute("UPDATE levels SET nword = ? WHERE user = ? AND guild = ?", (nword, author.id, guild.id))
                    await message.channel.send(f":thumbsdown:  \nNo racism!")

            if random.randint(1, 1000000) == 1: # 1, 1000000 / 1, 5
                level += 5
                await cursor.execute("UPDATE levels SET level = ? WHERE user = ? AND guild = ?", (level, author.id, guild.id))
                await cursor.execute("UPDATE levels SET xp = ? WHERE user = ? AND guild = ?", (0, author.id, guild.id))

                await message.channel.send(f"{author.mention} has discovered a one in a million easter egg and gained 5 extra levels!")
            else:
                pass

            await self.bot.db.commit()
            await self.bot.process_commands(message)

    # Make users in voice calls get xp every minute
    @tasks.loop(minutes=1.0)
    async def update_xp(self):
        for guild in self.bot.guilds:
            for voice_channel in guild.voice_channels:
                for member in voice_channel.members:
                    if not member.bot:
                        await self.give_xp(member, guild)
                        print(f"given {member} xp")
        
    async def give_xp(self, member, guild):
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT xp, level, money, bank, nword, skillpoints FROM levels WHERE user = ? AND guild = ?", (member.id, guild.id))
            result = await cursor.fetchone()
            
            if not result:
                await cursor.execute("INSERT INTO levels (level, xp, money, bank, user, guild, nword, skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)", (0, 0, 0, 0, member.id, guild.id, 0, 0, 0, 0, 0))
                await self.bot.db.commit()
                xp = 0
                level = 0
                money = 0
                bank = 0
                nword = 0
                skillpoints = 0
            else:
                xp, level, money, bank, nword, skillpoints = result

            xp += random.randint(25, 40) # 25, 40 / 100, 10000   per minute
            money += random.randint(30, 55) # 30, 55 / 1000, 10000   per minute

            await cursor.execute("UPDATE levels SET xp = ?, money = ? WHERE user = ? AND guild = ?", (xp, money, member.id, guild.id))

            xp_required = (level + 1) * 100

            if xp >= xp_required:
                level += 1
                skillpointsamount = 1 if level % 5 == 0 else 0
                skillpoints += skillpointsamount
                xp = 0  # Reset XP after level up

                await cursor.execute("UPDATE levels SET level = ?, xp = ?, skillpoints = ? WHERE user = ? AND guild = ?", (level, xp, skillpoints, member.id, guild.id))
                
                if skillpointsamount > 0:
                    #await member.send(f"Congratulations! You've leveled up to level {level} and gained {skillpointsamount} skill point(s)!")
                    pass
                else:
                    #await member.send(f"Congratulations! You've leveled up to level {level}!")
                    pass

            await self.bot.db.commit()

    # Define all of the app commands
    @app_commands.command(name="levelup", description="Level up by paying money.")
    async def levelup(self, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction)
        member = ctx.author

        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT xp FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            xp = await cursor.fetchone()
            await cursor.execute("SELECT level FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            level = await cursor.fetchone()
            await cursor.execute("SELECT money FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            money = await cursor.fetchone()
            await cursor.execute("SELECT bank FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            bank = await cursor.fetchone()
            await cursor.execute("SELECT skillpoints FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            skillpoints = await cursor.fetchone()

            if not xp or not level:
                await cursor.execute("INSERT INTO levels (level, xp, money, bank, user, guild, nword, skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)", (0, 0, 0, 0, member.id, ctx.guild.id, 0, 0, 0, 0, 0))
                await self.bot.commit()

            try:
                xp = xp[0]
                level = level[0]
                money = money[0]
                bank = bank[0]
                skillpoints = skillpoints[0]
            except TypeError:
                xp = 0
                level = 0
                money = 0
                bank = 0
                skillpoints = 0

            xp_required = (level + 1) * 100
            money_required = xp_required - xp

            # Make it cost 5 times more money to level up past lvl 100
            if level <= 100:
                money_required *= 10
            else:
                money_required *= 50

            if money >= money_required:
                level += 1

                if level % 5 == 0:
                    #skillpointsamount = level / 5
                    #skillpointsamount = int(skillpointsamount)
                    skillpointsamount = 1
                    skillpoints += skillpointsamount
                    await ctx.send(f"{member.mention} has paid {money_required} and has leveled up to level **{level}** and has gained **{skillpointsamount}** skill points!!")
                else:
                    await ctx.send(f"{member.mention} has paid {money_required} and has leveled up to level **{level}**!")

                money -= money_required
                await cursor.execute("UPDATE levels SET level = ? WHERE user = ? AND guild = ?", (level, member.id, ctx.guild.id))
                await cursor.execute("UPDATE levels SET xp = ? WHERE user = ? AND guild = ?", (0, member.id, ctx.guild.id))
                await cursor.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (money, member.id, ctx.guild.id))
                await cursor.execute("UPDATE levels SET skillpoints = ? WHERE user = ? AND guild = ?", (skillpoints, member.id, ctx.guild.id))
            else:
                await ctx.send(f"You don't have enough money for a new rank\nYou need {money_required} but you only have {money}", ephemeral=True)

        await self.bot.db.commit()

    @app_commands.command(name="deposit", description="Deposit a certain amount of money into your bank account.")
    async def deposit(self, interaction: discord.Interaction, amount: int):
        ctx = await self.bot.get_context(interaction)
        member = ctx.author

        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT xp FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            xp = await cursor.fetchone()
            await cursor.execute("SELECT level FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            level = await cursor.fetchone()
            await cursor.execute("SELECT money FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            money = await cursor.fetchone()
            await cursor.execute("SELECT bank FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            bank = await cursor.fetchone()

            if not xp or not level:
                await cursor.execute("INSERT INTO levels (level, xp, money, bank, user, guild, nword, skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)", (0, 0, 0, 0, member.id, ctx.guild.id, 0, 0, 0, 0, 0))
                await self.bot.commit()

            try:
                xp = xp[0]
                level = level[0]
                money = money[0]
                bank = bank[0]
            except TypeError:
                xp = 0
                level = 0
                money = 0
                bank = 0

            if money == 0:
                await ctx.send(f"You can't deposit nothing into your bank account", ephemeral=True)

            elif amount > money:
                await ctx.send(f"{member.mention} has deposited {money} into their bank account.")

                bank += money
                money -= money
                
                await cursor.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (money, member.id, ctx.guild.id))
                await cursor.execute("UPDATE levels SET bank = ? WHERE user = ? AND guild = ?", (bank, member.id, ctx.guild.id))

            elif amount <= 0:
                await ctx.send(f"You can't deposit nothing into your bank account", ephemeral=True)

            else:
                money -= amount
                bank += amount

                await cursor.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (money, member.id, ctx.guild.id))
                await cursor.execute("UPDATE levels SET bank = ? WHERE user = ? AND guild = ?", (bank, member.id, ctx.guild.id))

                await ctx.send(f"{member.mention} has deposited {amount} into their bank account.")
            
        await self.bot.db.commit()

    @app_commands.command(name="withdraw", description="Withdraw a certain amount of money from your bank account.")
    async def withdraw(self, interaction: discord.Interaction, amount: int):
        ctx = await self.bot.get_context(interaction)
        member = ctx.author

        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT xp FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            xp = await cursor.fetchone()
            await cursor.execute("SELECT level FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            level = await cursor.fetchone()
            await cursor.execute("SELECT money FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            money = await cursor.fetchone()
            await cursor.execute("SELECT bank FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            bank = await cursor.fetchone()

            if not xp or not level:
                await cursor.execute("INSERT INTO levels (level, xp, money, bank, user, guild, nword, skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)", (0, 0, 0, 0, member.id, ctx.guild.id, 0, 0, 0, 0, 0))
                await self.bot.commit()

            try:
                xp = xp[0]
                level = level[0]
                money = money[0]
                bank = bank[0]
            except TypeError:
                xp = 0
                level = 0
                money = 0
                bank = 0

            if bank <= 0:
                await ctx.send(f"You can't withdraw nothing from your bank account.", ephemeral=True)

            elif amount > bank:
                await ctx.send(f"{member.mention} has withdrawn {bank} from their bank account.")

                money += bank
                bank -= bank

                await cursor.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (money, member.id, ctx.guild.id))
                await cursor.execute("UPDATE levels SET bank = ? WHERE user = ? AND guild = ?", (bank, member.id, ctx.guild.id))

            elif amount <= 0:
                await ctx.send(f"You can't withdraw nothing from your bank account.", ephemeral=True)

            else:
                await ctx.send(f"{member.mention} has withdrawn {amount} from their bank account.")

                money += amount
                bank -= amount

                await cursor.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (money, member.id, ctx.guild.id))
                await cursor.execute("UPDATE levels SET bank = ? WHERE user = ? AND guild = ?", (bank, member.id, ctx.guild.id))

        await self.bot.db.commit()

    @app_commands.command(name="givemoney", description="Give a user a certain amount of money. (admin command)")
    async def givemoney(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        ctx = await self.bot.get_context(interaction)

        if interaction.user.guild_permissions.administrator:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT xp FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
                xp = await cursor.fetchone()
                await cursor.execute("SELECT level FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
                level = await cursor.fetchone()
                await cursor.execute("SELECT money FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
                money = await cursor.fetchone()
                await cursor.execute("SELECT bank FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
                bank = await cursor.fetchone()

                if not xp or not level:
                    await cursor.execute("INSERT INTO levels (level, xp, money, bank, user, guild, nword, skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)", (0, 0, 0, 0, member.id, ctx.guild.id, 0, 0, 0, 0, 0))
                    await self.bot.commit()

                try:
                    xp = xp[0]
                    level = level[0]
                    money = money[0]
                    bank = bank[0]
                except TypeError:
                    xp = 0
                    level = 0
                    money = 0
                    bank = 0

                if amount <= 0:
                    await interaction.response.send_message("You can't give the specified amount to the person. Amount can only be a positive number.", ephemeral=True)
                else:
                    money += amount
                    await cursor.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (money, member.id, ctx.guild.id))
                    await interaction.response.send_message(f"`{member}` now has **{money}** money and {bank} money in their bank.", ephemeral=True)

            await self.bot.db.commit()

        else:
            await interaction.response.send_message("You need the administrator permission to use this command.", ephemeral=True)

    @app_commands.command(name="takemoney", description="Take a certain amount of money from a user. (admin command)")
    async def takemoney(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        ctx = await self.bot.get_context(interaction)

        if interaction.user.guild_permissions.administrator:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT xp FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
                xp = await cursor.fetchone()
                await cursor.execute("SELECT level FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
                level = await cursor.fetchone()
                await cursor.execute("SELECT money FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
                money = await cursor.fetchone()
                await cursor.execute("SELECT bank FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
                bank = await cursor.fetchone()

                if not xp or not level:
                    await cursor.execute("INSERT INTO levels (level, xp, money, bank, user, guild, nword, skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)", (0, 0, 0, 0, member.id, ctx.guild.id, 0, 0, 0, 0, 0))
                    await self.bot.commit()

                try:
                    xp = xp[0]
                    level = level[0]
                    money = money[0]
                    bank = bank[0]
                except TypeError:
                    xp = 0
                    level = 0
                    money = 0
                    bank = 0

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
                        
                    await interaction.response.send_message(f"`{member}` now has **{money}** money and {bank} money in their bank.", ephemeral=True)

                await cursor.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (money, member.id, ctx.guild.id))
                await cursor.execute("UPDATE levels SET bank = ? WHERE user = ? AND guild = ?", (bank, member.id, ctx.guild.id))

            await self.bot.db.commit()

        else:
            await interaction.response.send_message("You need the administrator permission to use this command.", ephemeral=True)

    @app_commands.command(name="stats", description="Show a user's current statistics")
    async def stats(self, interaction: discord.Interaction, member: discord.Member = None):
        ctx = await self.bot.get_context(interaction)
        if member is None:
            member = ctx.author
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT xp FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            xp = await cursor.fetchone()
            await cursor.execute("SELECT level FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            level = await cursor.fetchone()
            await cursor.execute("SELECT money FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            money = await cursor.fetchone()
            await cursor.execute("SELECT bank FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            bank = await cursor.fetchone()
            await cursor.execute("SELECT skillpoints FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            skillpoints = await cursor.fetchone()

            if not xp or not level:
                await cursor.execute("INSERT INTO levels (level, xp, money, bank, user, guild, nword, skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)", (0, 0, 0, 0, member.id, ctx.guild.id, 0, 0, 0, 0, 0))
                await self.bot.commit()

            try:
                xp = xp[0]
                level = level[0]
                money = money[0]
                bank = bank[0]
                skillpoints = skillpoints[0]
            except TypeError:
                xp = 0
                level = 0
                money = 0
                bank = 0
                skillpoints = 0

            # Calculate xp needed for level up
            xp_required = (level + 1) * 100
            xp_left = xp_required - xp 

            em = discord.Embed(title=f"{member.name}'s Level", color=discord.Color.blurple(), description=f"Level : `{level}`\nXP: `{xp}`\nXP left : `{xp_left}`\nMoney in pocket : `{money}`\nMoney in bank : `{bank}`\nUnused Skillpoints : `{skillpoints}`")
            await ctx.send(embed=em)

    @app_commands.command(name="pickpocket", description="Rob a user for their money.")
    async def pickpocket(self, interaction: discord.Interaction, member: discord.Member):
        ctx = await self.bot.get_context(interaction)
        robber = ctx.author

        if member == ctx.author:
            await interaction.response.send_message("You can't rob yourself.", ephemeral=True)
        else:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT money FROM levels WHERE user = ? AND guild = ?", (robber.id, ctx.guild.id))
                moneyrobber = await cursor.fetchone()
                await cursor.execute("SELECT bank FROM levels WHERE user = ? AND guild = ?", (robber.id, ctx.guild.id))
                bankrobber = await cursor.fetchone()

                await cursor.execute("SELECT money FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
                moneymember = await cursor.fetchone()
                await cursor.execute("SELECT bank FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
                bankmember = await cursor.fetchone()

                await cursor.execute("SELECT skill_robfull_lvl FROM levels WHERE user = ? AND guild = ?", (robber.id, ctx.guild.id))
                skill_robfull_lvl = await cursor.fetchone()
                await cursor.execute("SELECT skill_robchance_lvl FROM levels WHERE user = ? AND guild = ?", (robber.id, ctx.guild.id))
                skill_robchance_lvl = await cursor.fetchone()

                if not moneyrobber:
                    await cursor.execute("INSERT INTO levels (level, xp, money, bank, user, guild, nword, skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)", (0, 0, 0, 0, robber.id, ctx.guild.id, 0, 0, 0, 0, 0))
                    await self.bot.commit()
                
                if not moneymember:
                    await cursor.execute("INSERT INTO levels (level, xp, money, bank, user, guild, nword, skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)", (0, 0, 0, 0, member.id, ctx.guild.id, 0, 0, 0, 0, 0))
                    await self.bot.commit()

                try:
                    moneyrobber = moneyrobber[0]
                    moneymember = moneymember[0]

                    bankrobber = bankrobber[0]
                    bankmember = bankmember[0]

                    skill_robfull_lvl = skill_robfull_lvl[0]
                    skill_robchance_lvl = skill_robchance_lvl[0]
                except TypeError:
                    moneyrobber = 0
                    moneymember = 0

                    bankrobber = 0
                    bankmember = 0

                    skill_robfull_lvl = 0
                    skill_robchance_lvl = 0


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

                            await interaction.response.send_message(f"{robber.mention} stole all money from {member.mention}!")
                        else:
                            robtake = moneymember * random.uniform(0.40, 0.75)
                            robtake = int(round(robtake, 0))

                            moneymember -= robtake
                            moneyrobber += robtake

                            await interaction.response.send_message(f"{robber.mention} stole {robtake} from {member.mention}!")

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

                        await interaction.response.send_message(f"{robber.mention} just got caught trying to pickpocket {member.mention} and got fined for {fine} money.")
                else:
                    await interaction.response.send_message("This user doesn't have enough money in their pocket. \n(500 money required)", ephemeral=True)

                await cursor.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (moneyrobber, robber.id, ctx.guild.id))
                await cursor.execute("UPDATE levels SET bank = ? WHERE user = ? AND guild = ?", (bankrobber, robber.id, ctx.guild.id))
                await cursor.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (moneymember, member.id, ctx.guild.id))
                await cursor.execute("UPDATE levels SET bank = ? WHERE user = ? AND guild = ?", (bankmember, member.id, ctx.guild.id))
            await self.bot.db.commit()
    
    @pickpocket.error
    async def on_pickpocket_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(str(error), ephemeral=True)

    @app_commands.command(name="heist", description="Rob a user for their bank money.")
    #@app_commands.checks.cooldown(1, 86400.0, key=lambda i: (i.guild_id, i.user.id)) # 24 hour cooldown
    async def heist(self, interaction: discord.Interaction, member: discord.Member):
        ctx = await self.bot.get_context(interaction)
        robber = ctx.author

        if member == ctx.author:
            await interaction.response.send_message("You can't rob yourself.", ephemeral=True)
        else:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT money FROM levels WHERE user = ? AND guild = ?", (robber.id, ctx.guild.id))
                moneyrobber = await cursor.fetchone()
                await cursor.execute("SELECT bank FROM levels WHERE user = ? AND guild = ?", (robber.id, ctx.guild.id))
                bankrobber = await cursor.fetchone()

                await cursor.execute("SELECT money FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
                moneymember = await cursor.fetchone()
                await cursor.execute("SELECT bank FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
                bankmember = await cursor.fetchone()

                await cursor.execute("SELECT skill_heistchance_lvl FROM levels WHERE user = ? AND guild = ?", (robber.id, ctx.guild.id))
                skill_heistchance_lvl = await cursor.fetchone()

                if not moneyrobber:
                    await cursor.execute("INSERT INTO levels (level, xp, money, bank, user, guild, nword, skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)", (0, 0, 0, 0, robber.id, ctx.guild.id, 0, 0, 0, 0, 0))
                    await self.bot.commit()
                
                if not moneymember:
                    await cursor.execute("INSERT INTO levels (level, xp, money, bank, user, guild, nword, skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)", (0, 0, 0, 0, member.id, ctx.guild.id, 0, 0, 0, 0, 0))
                    await self.bot.commit()

                try:
                    moneyrobber = moneyrobber[0]
                    moneymember = moneymember[0]

                    bankrobber = bankrobber[0]
                    bankmember = bankmember[0]

                    skill_heistchance_lvl = skill_heistchance_lvl[0]
                except TypeError:
                    moneyrobber = 0
                    moneymember = 0

                    bankrobber = 0
                    bankmember = 0

                    skill_heistchance_lvl = 0
                
                if bankmember >= 1000:
                    baseChance = 10 # 10% chance
                    baseChance += skill_heistchance_lvl * 1
                    chance = random.randint(1, 100)
                    if chance <= baseChance: # successful heist
                        take = bankmember * random.uniform(0.8, 1.0)
                        take = int(round(take, 0))

                        bankrobber += take
                        bankmember -= take

                        await interaction.response.send_message(f"{robber.mention} stole {take} from {member.mention}!")

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

                        await interaction.response.send_message(f"{robber.mention} just got caught trying to rob {member.mention} and got fined for {fine} money.")

                else:
                    await interaction.response.send_message("This user doesn't have enough money in their bank. \n(1000 money required)", ephemeral=True)

                await cursor.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (moneyrobber, robber.id, ctx.guild.id))
                await cursor.execute("UPDATE levels SET bank = ? WHERE user = ? AND guild = ?", (bankrobber, robber.id, ctx.guild.id))
                await cursor.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (moneymember, member.id, ctx.guild.id))
                await cursor.execute("UPDATE levels SET bank = ? WHERE user = ? AND guild = ?", (bankmember, member.id, ctx.guild.id))
            await self.bot.db.commit()

    @heist.error
    async def on_heist_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(str(error), ephemeral=True)
                
    @app_commands.command(name="work", description="Work to get money.")
    @app_commands.checks.cooldown(1, 900.0, key=lambda i: (i.guild_id, i.user.id))
    async def work(self, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction)
        member = ctx.author

        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT money FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            money = await cursor.fetchone()

            if not money:
                await cursor.execute("INSERT INTO levels (level, xp, money, bank, user, guild, nword, skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)", (0, 0, 0, 0, member.id, ctx.guild.id, 0, 0, 0, 0, 0))
                await self.bot.commit()

            try:
                money = money[0]
            except TypeError:
                money = 0

            paycheck = random.randint(300, 900)
            money += paycheck

            await interaction.response.send_message(f"{member.mention} went to work and has gained {paycheck} money.")

            await cursor.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (money, member.id, ctx.guild.id))
        await self.bot.db.commit()

    @work.error
    async def on_work_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(str(error), ephemeral=True)

    @app_commands.command(name="daily", description="Get your daily money bonus.")
    @app_commands.checks.cooldown(1, 86400.0, key=lambda i: (i.guild_id, i.user.id))
    async def daily(self, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction)
        member = ctx.author

        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT money FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            money = await cursor.fetchone()

            if not money:
                await cursor.execute("INSERT INTO levels (level, xp, money, bank, user, guild, nword, skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)", (0, 0, 0, 0, member.id, ctx.guild.id, 0, 0, 0, 0, 0))
                await self.bot.commit()

            try:
                money = money[0]
            except TypeError:
                money = 0

            dailyreward = round(random.randint(1500, 2500), -2)
            money += dailyreward

            await interaction.response.send_message(f"{member.mention} has gained {dailyreward} money from their daily reward.")

            await cursor.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (money, member.id, ctx.guild.id))
        await self.bot.db.commit()

    @daily.error
    async def on_daily_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(str(error), ephemeral=True)

    @app_commands.command(name="sendmoney", description="Give a user a certain amount of money.")
    async def sendmoney(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        ctx = await self.bot.get_context(interaction)
        sender = ctx.author

        if member == sender:
            await interaction.response.send_message(f"You can't send {amount} money to yourself.", ephemeral=True)
        else:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT money FROM levels WHERE user = ? AND guild = ?", (sender.id, ctx.guild.id))
                moneysender = await cursor.fetchone()
                await cursor.execute("SELECT money FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
                moneymember = await cursor.fetchone()

                if not moneysender:
                    await cursor.execute("INSERT INTO levels (level, xp, money, bank, user, guild, nword, skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)", (0, 0, 0, 0, sender.id, ctx.guild.id, 0, 0, 0, 0, 0))
                    await self.bot.commit()

                if not moneymember:
                    await cursor.execute("INSERT INTO levels (level, xp, money, bank, user, guild, nword, skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)", (0, 0, 0, 0, member.id, ctx.guild.id, 0, 0, 0, 0, 0))
                    await self.bot.commit()

                try:
                    moneysender = moneysender[0]
                    moneymember = moneymember[0]
                except TypeError:
                    moneysender = 0
                    moneymember = 0


                if amount <= 0:
                    await interaction.response.send_message("You can't give the specified amount to the person. Amount can only be a positive number.", ephemeral=True)
                else:
                    if moneysender < amount:
                        await interaction.response.send_message(f"You can't send {amount} money because you don't have enough.", ephemeral=True)
                    else:
                        moneysender -= amount
                        moneymember += amount

                        await interaction.response.send_message(f"{sender.mention} gave {amount} to {member.mention}.")

                await cursor.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (moneysender, sender.id, ctx.guild.id))
                await cursor.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (moneymember, member.id, ctx.guild.id))
        await self.bot.db.commit()
    
    @app_commands.command(name="bet", description="Bet on a number ranging from 1 to 3.")
    async def bet(self, interaction: discord.Interaction, amount: int, bet: int):
        ctx = await self.bot.get_context(interaction)
        member = ctx.author

        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT money FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            money = await cursor.fetchone()

            if not money:
                await cursor.execute("INSERT INTO levels (level, xp, money, bank, user, guild, nword, skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)", (0, 0, 0, 0, member.id, ctx.guild.id, 0, 0, 0, 0, 0))
                await self.bot.commit()

            try:
                money = money[0]
            except TypeError:
                money = 0

            if amount > money:
                await interaction.response.send_message(f"You can't bet {amount} money because you dont have enough.", ephemeral=True)
            else:
                rng = random.randint(1, 3)
                if bet == rng:
                    money += amount
                    await interaction.response.send_message(f"{member.mention} bet {amount} money on {bet} and won.")
                else:
                    money -= amount
                    await interaction.response.send_message(f"{member.mention} bet {amount} money on {bet} and lost. The number was {rng}")

            await cursor.execute("UPDATE levels SET money = ? WHERE user = ? AND guild = ?", (money, member.id, ctx.guild.id))
        await self.bot.db.commit()

    @app_commands.command(name="skills", description="Shows your skilltree.")
    async def skills(self, interaction: discord.Interaction):
        # Loads the stats needed
        ctx = await self.bot.get_context(interaction)
        member = ctx.author
        
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT xp FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            xp = await cursor.fetchone()
            await cursor.execute("SELECT level FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            level = await cursor.fetchone()
            await cursor.execute("SELECT skillpoints FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            skillpoints = await cursor.fetchone()
            await cursor.execute("SELECT skill_robfull_lvl FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            skill_robfull_lvl = await cursor.fetchone()
            await cursor.execute("SELECT skill_robchance_lvl FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            skill_robchance_lvl = await cursor.fetchone()
            await cursor.execute("SELECT skill_heistchance_lvl FROM levels WHERE user = ? AND guild = ?", (member.id, ctx.guild.id))
            skill_heistchance_lvl = await cursor.fetchone()

            if not xp or not level:
                await cursor.execute("INSERT INTO levels (level, xp, money, bank, user, guild, nword, skillpoints, skill_robfull_lvl, skill_robchance_lvl, skill_heistchance_lvl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (0, 0, 0, 0, member.id, ctx.guild.id, 0, 0, 0, 0, 0))
                await self.bot.db.commit()

            try:
                skillpoints = skillpoints[0]
                skill_robfull_lvl = skill_robfull_lvl[0]
                skill_robchance_lvl = skill_robchance_lvl[0]
                skill_heistchance_lvl = skill_heistchance_lvl[0]
            except TypeError:
                skillpoints = 0
                skill_robfull_lvl = 0
                skill_robchance_lvl = 0
                skill_heistchance_lvl = 0

            levelRobbing = skill_heistchance_lvl + skill_robchance_lvl + skill_robfull_lvl

            # Discord embeds that shows the skill tree
            embedMain = discord.Embed(
                title="Skill Category Tree",
                description=f"Skillpoints : `{skillpoints}`\n\n**R**obbing : `{levelRobbing}`",
                color=discord.Color.blurple()
            )
            embedRobbing = discord.Embed(
                title="Robbing Category Tree",
                description=f"Skillpoints : `{skillpoints}`\nLevel : `{levelRobbing}` \n\n1.Full Rob Chance LVL : `{skill_robfull_lvl}`\n2.Rob Chance LVL : `{skill_robchance_lvl}`\n3.Heist Chance LVL : `{skill_heistchance_lvl}`",
                color=discord.Color.red()
            )


            # Make a view for the buttons
            viewMain = discord.ui.View(timeout=None)
            viewRobbing = discord.ui.View(timeout=None)


            # Robbing button skilltree
            button_robbing = discord.ui.Button(style=discord.ButtonStyle.red, label="R")

            button_robbing1 = discord.ui.Button(style=discord.ButtonStyle.red, label="1")
            button_robbing2 = discord.ui.Button(style=discord.ButtonStyle.red, label="2")
            button_robbing3 = discord.ui.Button(style=discord.ButtonStyle.red, label="3")

            button_back = discord.ui.Button(style=discord.ButtonStyle.red, label="Back")


            # Add the buttons to the view
            viewMain.add_item(button_robbing)

            viewRobbing.add_item(button_robbing1)
            viewRobbing.add_item(button_robbing2)
            viewRobbing.add_item(button_robbing3)
            viewRobbing.add_item(button_back)

            # Make the callbacks for the buttons
            async def callback_robbing(interaction: discord.Interaction):
                await interaction.response.send_message(embed=embedRobbing, view=viewRobbing, ephemeral=True)
            button_robbing.callback = callback_robbing


            # Make the callbacks for using the skillpoints
            async def callback_robbing1(interaction: discord.Interaction):
                nonlocal skillpoints, skill_robfull_lvl

                if skillpoints > 0:
                    if skill_robfull_lvl <= 5:
                        skillpoints -= 1
                        skill_robfull_lvl += 1
                        
                        # Update database
                        async with self.bot.db.cursor() as cursor:
                            await cursor.execute("UPDATE levels SET skillpoints = ? WHERE user = ? AND guild = ?", (skillpoints, member.id, ctx.guild.id))
                            await cursor.execute("UPDATE levels SET skill_robfull_lvl = ? WHERE user = ? AND guild = ?", (skill_robfull_lvl, member.id, ctx.guild.id))
                            await self.bot.db.commit()

                        # Refresh everything
                        levelRobbing = skill_heistchance_lvl + skill_robchance_lvl + skill_robfull_lvl
                        embedMain.description = f"Skillpoints : `{skillpoints}`\n\n**R**obbing : `{levelRobbing}`"
                        embedRobbing.description = f"Skillpoints : `{skillpoints}`\nLevel : `{levelRobbing}` \n\n1.Full Rob Chance LVL : `{skill_robfull_lvl}`\n2.Rob Chance LVL : `{skill_robchance_lvl}`\n3.Heist Chance LVL : `{skill_heistchance_lvl}`"
                        await interaction.response.edit_message(embed=embedRobbing, view=viewRobbing)
                    else:
                        await interaction.response.send_message(f"You already reached the maximum level for this stat.", ephemeral=True)
                else:
                    await interaction.response.send_message(f"You don't have enough Skillpoints.", ephemeral=True)
            button_robbing1.callback = callback_robbing1

            async def callback_robbing2(interaction: discord.Interaction):
                nonlocal skillpoints, skill_robchance_lvl

                if skillpoints > 0:
                    if skill_robchance_lvl <= 5:
                        skillpoints -= 1
                        skill_robchance_lvl += 1
                        
                        # Update database
                        async with self.bot.db.cursor() as cursor:
                            await cursor.execute("UPDATE levels SET skillpoints = ? WHERE user = ? AND guild = ?", (skillpoints, member.id, ctx.guild.id))
                            await cursor.execute("UPDATE levels SET skill_robchance_lvl = ? WHERE user = ? AND guild = ?", (skill_robchance_lvl, member.id, ctx.guild.id))
                            await self.bot.db.commit()

                        # Refresh everything
                        levelRobbing = skill_heistchance_lvl + skill_robchance_lvl + skill_robfull_lvl
                        embedMain.description = f"Skillpoints : `{skillpoints}`\n\n**R**obbing : `{levelRobbing}`"
                        embedRobbing.description = f"Skillpoints : `{skillpoints}`\nLevel : `{levelRobbing}` \n\n1.Full Rob Chance LVL : `{skill_robfull_lvl}`\n2.Rob Chance LVL : `{skill_robchance_lvl}`\n3.Heist Chance LVL : `{skill_heistchance_lvl}`"
                        await interaction.response.edit_message(embed=embedRobbing, view=viewRobbing)
                    else:
                        await interaction.response.send_message(f"You already reached the maximum level for this stat.", ephemeral=True)
                else:
                    await interaction.response.send_message(f"You don't have enough Skillpoints.", ephemeral=True)
            button_robbing2.callback = callback_robbing2
            
            async def callback_robbing3(interaction: discord.Interaction):
                nonlocal skillpoints, skill_heistchance_lvl

                if skillpoints > 0:
                    if skill_heistchance_lvl <= 5:
                        skillpoints -= 1
                        skill_heistchance_lvl += 1
                        
                        # Update database
                        async with self.bot.db.cursor() as cursor:
                            await cursor.execute("UPDATE levels SET skillpoints = ? WHERE user = ? AND guild = ?", (skillpoints, member.id, ctx.guild.id))
                            await cursor.execute("UPDATE levels SET skill_heistchance_lvl = ? WHERE user = ? AND guild = ?", (skill_heistchance_lvl, member.id, ctx.guild.id))
                            await self.bot.db.commit()

                        # Refresh everything
                        levelRobbing = skill_heistchance_lvl + skill_robchance_lvl + skill_robfull_lvl
                        embedMain.description = f"Skillpoints : `{skillpoints}`\n\n**R**obbing : `{levelRobbing}`"
                        embedRobbing.description = f"Skillpoints : `{skillpoints}`\nLevel : `{levelRobbing}` \n\n1.Full Rob Chance LVL : `{skill_robfull_lvl}`\n2.Rob Chance LVL : `{skill_robchance_lvl}`\n3.Heist Chance LVL : `{skill_heistchance_lvl}`"
                        await interaction.response.edit_message(embed=embedRobbing, view=viewRobbing)
                    else:
                        await interaction.response.send_message(f"You already reached the maximum level for this stat.", ephemeral=True)
                else:
                    await interaction.response.send_message(f"You don't have enough Skillpoints.", ephemeral=True)
            button_robbing3.callback = callback_robbing3


            # Button for going back
            async def callback_back(interaction: discord.Interaction):
                await interaction.response.send_message(embed=embedMain, view=viewMain, ephemeral=True)
            button_back.callback = callback_back

        await interaction.response.send_message(embed=embedMain, view=viewMain, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Economy(bot))
