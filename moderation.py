import discord
from discord.ui import View, Select, Button
from discord.ext import commands
import json
import pymongo
import os

testing_servers = [1038227549198753862, 1044711937956651089, 821083375728853043]

client = pymongo.MongoClient(
     f"mongodb+srv://BlueRobin:{os.getenv('MONGOPASS')}@nestling-bot-settings.8n1wpmw.mongodb.net/?retryWrites=true&w=majority")
db = client.moderation


class warning(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    # noinspection PyUnresolvedReferences
    @commands.slash_command(name="warn", description="Warn a user.")
    async def warn(self, ctx, member: discord.Option(discord.Member, description="What member do you want to warn?"),
                   reason: discord.Option(str, description="Why do you want to warn this user?", required=False)):
        coll = db.warns
        if ctx.author.guild_permissions.manage_guild:
            embed = discord.Embed(
                title=f"{ctx.author.name} warned you",
                colour=discord.Colour.random(),
                description=f"{member.mention} \n Reason is: {reason}",
            )
            await ctx.respond(embed=embed)
            try:
                coll.insert_one({"_id": {"guild": ctx.guild.id, "user": member.id}, "amount": 1})
            except pymongo.errors.DuplicateKeyError:
                # print(coll.find_one({"_id": {"guild": ctx.guild.id}, "users"}))
                coll.update_one({"_id": {"guild": ctx.guild.id, "user": member.id}, "$inc": {"amount": 1}})
        else:
            await ctx.respond("You don't have permission to do that.", ephemeral=True)

    @commands.slash_command(name="warns", description="See all warns")
    async def warns(self, ctx):
        coll = db.warns
        users = coll.find({})
        end_str = ""
        for user in users:
            if user["_id"]["guild"] == ctx.guild.id:
                end_str += f"Member: {ctx.guild.get_member(user['_id']['user'])} has {user['amount']} warn(s)\n"
        embed = discord.Embed(
            title="Server warns",
            description=end_str,
            color=discord.Color.random()
        )
        if not end_str:
            embed = discord.Embed(
                title="This server doesn't have any warns.",
                color=discord.Color.random()
            )

        await ctx.respond(embed=embed)

    @commands.slash_command(name="unwarn", description="Unwarn a user.")
    async def unwarn(self, ctx, user: discord.Option(discord.Member),
                     amount: discord.Option(int, min_value=1, default=1)):
        if user.guild_permissions.manage_guild:
            coll = db.warns
            if amount < 1:
                await ctx.respond("Unwarn amount must be greater than one.", ephemeral=True)
                return 0
            try:
                coll.update_one({"_id": {"guild": user.guild.id, "user": user.id}}, {"$inc": {"amount": -amount}})
                if coll.find_one({"_id": {"guild": user.guild.id, "user": user.id}})["amount"] <= 0:
                    coll.delete_one({"_id": {"guild": user.guild.id, "user": user.id}})
                embed = discord.Embed(
                    title="Removed warn",
                    description=f"Removed warn(s) for {user.mention} \n Removed {amount} warn(s)",
                    color=discord.Color.random()
                )
            except TypeError:
                embed = discord.Embed(
                    title="This server doesn't have any warns.",
                    color=discord.Color.random()
                )

            await ctx.respond(embed=embed)
        else:
            await ctx.respond("You don't have permission to do that!", ephemeral=True)


class ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="ban", description="Banning is fun!")
    async def ban(self, ctx, user: discord.Option(discord.Member), reason: discord.Option(str)):
        if user == self.bot.user:
            await ctx.respond("Hey! You can't do that...")
        elif ctx.user.guild_permissions.ban_members:
            await user.ban(reason=reason)
            await ctx.respond(f"Banned {user.name} from {ctx.guild}!")
        else:
            await ctx.respond("You don't have the permissions to do that.", ephemeral=True)

    @ban.error
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        await ctx.respond(f"I couldn't ban that user. Check permissions. \n > ||ERROR: {error} ||", ephemeral=True)


class unbanButton(Button):
    def __init__(self, row, emoji, user, users, message):
        super().__init__(style=discord.ButtonStyle.blurple, emoji=emoji, row=row)
        self.users = users
        self.user = user
        self.message = message

    async def callback(self, interaction):
        if self.user == interaction.user:
            self.view.disable_all_items()
            await self.message.edit_original_response(view=self.view)
            await interaction.response.send_message(f"Unbanning...")
            for user in self.users:
                await interaction.guild.unban(user)
                await interaction.channel.send(f"Unbanned {user.name} from {interaction.guild.name}!")
        else:
            await interaction.response.send_message(f"Not your command. Try /bans")


class bans(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="bans", description="Let's take a look!")
    async def bans(self, ctx):
        bansList = ""
        index = 0
        optionsList = []
        banList2 = []
        try:
            async for i in ctx.guild.bans():
                index += 1
                bansList += f"{index}: {i.user.name}"
                bansList += "\n"
                banList2.append(i.user)
                optionsList.append(discord.SelectOption(label=i.user.name, description="Unban this user.", emoji="🔨"))
        except discord.errors.Forbidden:
            await ctx.respond('I am not allowed to see bans', ephemeral=True)

        async def callback(interaction):
            if interaction.user.guild_permissions.ban_members:

                index = 0
                selectValues = ""
                for i in select.values:
                    index += 1
                    selectValues += f"{index}: {i}"
                    selectValues += "\n"
                embed = discord.Embed(
                    title=f"Are you sure you want to unban these users?",
                    description=selectValues
                )
                message = await interaction.response.send_message(embed=embed)
                view = View()
                view.add_item(unbanButton(0, "✅", user=interaction.user, users=banList2, message=interaction))
                await message.edit_original_response(view=view)
            else:
                await interaction.response.send_message("You don't have permission to do that!", ephemeral=True)

        try:
            select = Select(min_values=1, max_values=len(optionsList), options=optionsList)
        except ValueError as error:
            await ctx.respond(f"There are no bans, or I don't have permission. \n > ||ERROR: {error} ||",
                              ephemeral=True)
            return
        view = View()
        view.add_item(select)
        embed = discord.Embed(
            title="Bans",
            description=bansList,
            color=discord.Color.random()
        )
        select.callback = callback
        message = await ctx.respond(embed=embed)
        await message.edit_original_response(view=view)

    @bans.error
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error):
        await ctx.respond(f"There are no bans, or I don't have permission. \n > ||ERROR: {error} ||", ephemeral=True)
