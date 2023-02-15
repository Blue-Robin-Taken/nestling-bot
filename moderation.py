import discord
from discord.ui import View, Select, Button
from discord.ext import commands
import json
import pymongo

testing_servers = [1038227549198753862, 1044711937956651089, 821083375728853043]

client = pymongo.MongoClient(
    "mongodb+srv://BlueRobin:ZaJleEpNhBUxqMDK@nestling-bot-settings.8n1wpmw.mongodb.net/?retryWrites=true&w=majority")
db = client.moderation


class warning(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    # noinspection PyUnresolvedReferences
    @commands.slash_command(name="warn", description="Warn a user.")
    async def warn(self, ctx, member: discord.Option(discord.Member, description="What member do you want to warn?"),
                   reason: str):
        coll = db.warns
        if ctx.author.guild_permissions.manage_guild:
            embed = discord.Embed(
                title=f"{ctx.author.name} warned you",
                colour=discord.Colour.random(),
                description=f"{member.mention} \n Reason is: {reason}",
            )
            await ctx.respond(embed=embed)
            try:
                coll.insert_one({"_id": {"guild": ctx.guild.id}, "users": [{str(member.id): 1}]})
            except pymongo.errors.DuplicateKeyError:

                coll.update_one({"_id": {"guild": ctx.guild.id}}, {"$inc": {str(member.id): 1}})
        else:
            await ctx.respond("You don't have permission to do that.", ephemeral=True)

    @commands.slash_command(name="warns", description="See all warns")
    async def warns(self, ctx):
        coll = db.warns
        if not list(coll.find({"_id": {'guild': ctx.guild.id}})) == []:
            warns = list(coll.find({"_id": {'guild': ctx.guild.id}}))
            userText = ""
            print(warns)
            for user in warns[0].keys():
                print(user)
                if user != "_id":
                    user_name = await self.bot.fetch_user(user)
                    print(user_name)
                else:
                    continue
                warn_amount = warns[0][str(user)]
                userText += f"{user_name} has {warn_amount} warn(s). \n"
            if userText != "":
                embed = discord.Embed(
                    title=f"Warns for {ctx.guild.name}",
                    colour=discord.Colour.random(),
                    description=userText,
                )
                await ctx.respond(embed=embed)
            else:
                await ctx.respond("There are no warns in this server.", ephemeral=True)
        else:
            await ctx.respond("There are no warns in this server.", ephemeral=True)

    @commands.slash_command(name="unwarn", description="Unwarn a user.")
    async def unwarn(self, ctx, member: discord.Option(discord.Member),
                     amount: discord.Option(int, min_value=1, default=1)):
        coll = db.warns
        if not coll.find_one({"_id": {"guild": ctx.guild.id}}, {str(member.id)}) is None:
            if list(coll.find_one({"_id": {"guild": ctx.guild.id}}, {str(member.id)})):
                coll.update_one({"_id": {"guild": ctx.guild.id}}, {"$inc": {str(member.id): -amount}})
                find_list = list(coll.find({"_id": {"guild": ctx.guild.id}}, {str(member.id)}))[0]
                x = coll.delete_one({'_id': {'guild': 1044711937956651089}, '497930397985013781': -5})
                await ctx.respond(f"{member.mention} has been unwarned.")
            else:
                await ctx.respond(f"{member.mention} has been unwarned.")
        else:
            await ctx.respond(f"{member.mention} has no warns", ephemeral=True)


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
        async for i in ctx.guild.bans():
            index += 1
            bansList += f"{index}: {i.user.name}"
            bansList += "\n"
            banList2.append(i.user)
            optionsList.append(discord.SelectOption(label=i.user.name, description="Unban this user.", emoji="🔨"))

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
