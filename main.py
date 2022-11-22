import discord
from discord.ui import Button, View, Select
import random
import asyncio
import twentyfortyeight
from discord.ext import commands
import json

bot = discord.Bot()
testing_servers = [1038227549198753862, 1044711937956651089]


@bot.event
async def on_ready():
    print('ready')


@bot.slash_command(guild_ids=testing_servers, name='ping', description='Test if the bot is online!')
async def ping(ctx):
    await ctx.respond('Pong!')


@bot.slash_command(guild_ids=testing_servers, name="eightball", description="Fun 8ball command!")
async def eightball(ctx, question: discord.Option(str, description="Ask me anything!")):
    random.seed(str(ctx.user.id) + question)
    responses = ["Maybe.", "I have no idea.", "I think so.", "Yes.", "Why would you ask that?", "No.", "Yes.",
                 "Probably.", "Funny.", "Who are you again?", "When is lunch?", "Yes 1+1 is two. So, yes.",
                 "Maybe go see a therapist.", "Lol.", "I wish.", "Imagine."]
    random_self = random.randint(0, len(responses) - 1)

    embed = discord.Embed(
        color=discord.Color.red(),
        title="Eightball",
        description=f"""
    **My answer**:
    {responses[random_self]}

    **You asked**:
    {str(question)}

    """
    )
    await ctx.respond(embed=embed)


class approvebutton(Button):
    def __init__(self, row, emoji):
        super().__init__(style=discord.ButtonStyle.blurple, emoji=emoji, row=row)

    async def callback(self, interaction):
        embed = discord.Embed(
            color=discord.Color.red(),
            title=f"ERROR",
        )
        if interaction.user.guild_permissions.manage_guild:
            if self.emoji.name == "✅":
                embed = discord.Embed(
                    color=discord.Color.green(),
                    title=f"Messaged Approved!",
                    description=f"This message was approved by {interaction.user.name}"
                )
            elif self.emoji.name == "❌":
                embed = discord.Embed(
                    color=discord.Color.red(),
                    title=f"Messaged Rejected!",
                    description=f"This message was rejected by {interaction.user.name}"
                )
            await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            embed = discord.Embed(
                color=discord.Color.red(),
                title=f"You don't have the permissions to do that!",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.slash_command(guild_ids=testing_servers, name="suggest",
                   description="Suggest something in the art-suggestion channel!")
async def suggest(ctx, suggestion: discord.Option(str, description="Suggest anything!")):
    await ctx.respond("Sending message!", ephemeral=True)
    embed = discord.Embed(
        color=discord.Color.red(),
        title=f"Suggestion by {ctx.author.name}",
        description=f"{suggestion}",
    )
    channel = bot.get_channel(1038260886634233896)
    message = await channel.send(embed=embed)
    view = View()
    view.add_item(approvebutton(0, "✅"))
    view.add_item(approvebutton(0, "❌"))
    await message.edit(view=view)


class AnnounceButton(Button):
    def __init__(self, row, emoji, channel, message, self_message):
        super().__init__(style=discord.ButtonStyle.blurple, emoji=emoji, row=row)
        self.channel = channel
        self.message = message
        self.message_self = self_message

    async def callback(self, interaction):
        self.view.disable_all_items()
        await self.message_self.edit(view=self.view)
        if self.emoji.name == "✅":
            embed = discord.Embed(
                color=discord.Color.green(),
                title=f"Sending announcement!",
                description=f"Sending..."
            )
            await self.channel.send(embed=self.message)
        elif self.emoji.name == "❌":
            embed = discord.Embed(
                color=discord.Color.red(),
                title=f"Announcement canceled!",
                description=f"```If you think this was a bug, please talk to the developer.```")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.slash_command(guild_ids=testing_servers, name="announce", description="Make server announcements!")
async def announce(ctx, channel: discord.Option(str,
                                                description="Copy the text channel in developer mode, or just use the # system."),
                   title: str, text: str):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("You do not have the permissions to do that!")
        return

        # response embed
    try:
        channel = bot.get_channel(int(channel))
    except ValueError:
        channel = bot.get_channel(int(''.join(char for char in channel if char.isdigit())))
        # announcement embed
    newText = text.replace("~", "\n")
    embed_check = discord.Embed(
        colour=discord.Colour.red(),
        title=title,
        description=newText
    )
    print(newText)

    await ctx.respond(embed=embed_check)
    message = await ctx.channel.send("Is this correct?")
    view = View()
    view.add_item(AnnounceButton(0, "✅", channel, embed_check, message))
    view.add_item(AnnounceButton(0, "❌", channel, embed_check, message))
    await message.edit(view=view)


class TwentyFortyEightButton(Button):
    def __init__(self, row, emoji, game, user, color):
        super().__init__(style=discord.ButtonStyle.blurple, emoji=emoji, row=row)
        self.game = game
        self.user = user
        self.color = color

    async def callback(self, interaction):
        if self.user == interaction.user:
            if self.emoji.name == "▶":
                self.game.Right()
            elif self.emoji.name == "◀":
                self.game.Left()
            elif self.emoji.name == "🔼":
                self.game.Up()
            elif self.emoji.name == "🔽":
                self.game.Down()
            embed = discord.Embed(
                title="2048",
                description=twentyfortyeight.DecryptBoard(self.game.boardList),
                colour=discord.Colour.random()
            )
            embed.set_author(name=self.user, icon_url=self.user.avatar.url)
            embed.set_footer(text=f"Score: {self.game.score}")
            await interaction.message.edit(
                embed=embed)
            await interaction.response.defer()
        else:
            await interaction.response.send_message("This is not your game!", ephemeral=True)


@bot.slash_command(guild_ids=testing_servers, name="2048", description="Play 2048 on Discord!")
async def twentyfortyeightcommand(ctx):
    game = twentyfortyeight.TwentyFortyEight(False)
    string = twentyfortyeight.DecryptBoard(game.boardList)
    embed = discord.Embed(
        title="2048",
        description=string,
        colour=discord.Colour.random()
    )
    embed.set_author(name=ctx.user, icon_url=ctx.user.avatar.url)
    embed.set_footer(text=f"Score: {game.score}")

    message = await ctx.respond(embed=embed)
    view = View(timeout=600)
    view.add_item(TwentyFortyEightButton(0, "🔼", game, ctx.user, False))
    view.add_item(TwentyFortyEightButton(0, "🔽", game, ctx.user, False))
    view.add_item(TwentyFortyEightButton(0, "◀", game, ctx.user, False))
    view.add_item(TwentyFortyEightButton(0, "▶", game, ctx.user, False))

    await message.edit_original_response(view=view)


@bot.slash_command(guild_ids=testing_servers, name="ban", description="Banning is fun!")
async def ban(ctx, user: discord.Option(discord.Member), reason: discord.Option(str)):
    if user == bot.user:
        await ctx.respond("Hey! You can't do that...")
    elif ctx.user.guild_permissions.ban_members:
        await user.ban(reason=reason)
        await ctx.respond(f"Banned {user.name} from {ctx.guild}!")
    else:
        await ctx.respond("You don't have the permissions to do that.", ephemeral=True)


@ban.error
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
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


@bot.slash_command(guild_ids=testing_servers, name="bans", description="Let's take a look!")
async def bans(ctx):
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

    select = Select(min_values=1, max_values=len(optionsList), options=optionsList)
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
async def on_application_command_error(ctx: discord.ApplicationContext, error):
    await ctx.respond(f"There are no bans, or I don't have permission. \n > ||ERROR: {error} ||", ephemeral=True)


class settingsButton(Button):
    def __init__(self, row, label, default, key):
        super().__init__(style=discord.ButtonStyle.blurple, label=label, row=row)
        self.default = default
        self.key = key

    async def callback(self, interaction):
        message = await interaction.response.send_message(self.key)
        channels = bot.get_all_channels()
        options_list = []
        for channel in channels:
            print(channel.permissions_for(bot.user.roles))
            print(channel.name)
            options_list.append(discord.SelectOption(label=channel.name, emoji="📜"))
        view = View()
        view.add_item(Select(options=options_list, max_values=1, min_values=1))
        await message.edit_original_response(view=view)


@bot.slash_command(guild_ids=testing_servers, name="settings", description="Change some settings.")
async def settings(ctx):
    defaultSettingsList = {"Suggestion Channel": None}
    embed = discord.Embed(
        title="Settings",
        description="Select a setting: ",
        color=discord.Color.random()
    )
    index = 0
    for i in defaultSettingsList.keys():  # Create embed of all the settings
        index += 1
        embed.add_field(name=f"{index}:", value=i, inline=False)
    message = await ctx.respond("Select a setting: ", embed=embed)
    view = View()  # Set view

    index = 0
    for i in defaultSettingsList.keys():  # Create buttons for all settings
        index += 1
        view.add_item(settingsButton(0, str(index), defaultSettingsList, i))
    await message.edit_original_response(view=view)  # Edit view into message


bot.run("MTA0NDMyMDUwNjk0MzM3NzQzOQ.GKrhD8.P2ggiWUov9lY9DHv6Gxc4scuyUtC6UeAIH09q8")
