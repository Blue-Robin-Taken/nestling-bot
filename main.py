import discord
import requests
from discord.ui import Button, View, Select
import random
import asyncio
import twentyfortyeight
import feedparser
from discord.ext import commands
import json
import random
from random import choice
from bs4 import BeautifulSoup
import re

bot = discord.Bot()
testing_servers = [1038227549198753862, 1044711937956651089, 821083375728853043]


@bot.event
async def on_ready():
    print('ready')


@bot.slash_command(name='ping', description='Test if the bot is online!')
async def ping(ctx):
    await ctx.respond('Pong!')


@bot.slash_command(name="eightball", description="Fun 8ball command!")
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
    def __init__(self, row, emoji, message):
        super().__init__(style=discord.ButtonStyle.blurple, emoji=emoji, row=row)
        self.message_self = message

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
            self.view.disable_all_items()
            await self.message_self.edit(view=self.view)
            await interaction.response.send_message(embed=embed, ephemeral=False)

        else:
            embed = discord.Embed(
                color=discord.Color.red(),
                title=f"You don't have the permissions to do that!",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.slash_command(name="suggest",
                   description="Suggest something in the art-suggestion channel!")
async def suggest(ctx, suggestion: discord.Option(str, description="Suggest anything!")):
    error = False
    embed = discord.Embed(
        color=discord.Color.red(),
        title=f"Suggestion by {ctx.author.name}",
        description=f"{suggestion}",
    )
    with open("settings.json", "r") as f:
        try:
            file = json.load(f)
            channel = bot.get_channel(int(file[str(ctx.guild.id)]["Suggestion Channel"]))
        except KeyError:
            await ctx.respond("There isn't a suggestion channel set. Use /settings to set one.", ephemeral=True)
            error = True
    if not error:
        await ctx.respond("Sending message!", ephemeral=True)
        message = await channel.send(embed=embed)
        view = View()
        view.add_item(approvebutton(0, "✅", message))
        view.add_item(approvebutton(0, "❌", message))
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


@bot.slash_command(name="announce", description="Make server announcements!")
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


@bot.slash_command(name="2048", description="Play 2048 on Discord!")
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
    view = View(timeout=None)
    view.add_item(TwentyFortyEightButton(0, "🔼", game, ctx.user, False))
    view.add_item(TwentyFortyEightButton(0, "🔽", game, ctx.user, False))
    view.add_item(TwentyFortyEightButton(0, "◀", game, ctx.user, False))
    view.add_item(TwentyFortyEightButton(0, "▶", game, ctx.user, False))

    await message.edit_original_response(view=view)


@bot.slash_command(name="ban", description="Banning is fun!")
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


@bot.slash_command(name="bans", description="Let's take a look!")
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
    def __init__(self, row, label, default, key, user):
        super().__init__(style=discord.ButtonStyle.blurple, label=label, row=row)
        self.default = default
        self.key = key
        self.user = user

    async def callback(self, interaction):
        if interaction.user == self.user:
            message = await interaction.response.send_message(self.key)
            categories = interaction.guild.categories
            options_list = []
            selects = []
            index = 0
            selects.append(Select(options=options_list))
            for category in categories:
                for channel in category.channels:
                    index += 1
                    if index > 20:
                        index = 0
                        selects.append(Select(options=options_list))
                        options_list = []
                    else:
                        if str(channel.type) == "text":
                            options_list.append(discord.SelectOption(label=channel.name, emoji="📜"))
            view = View()

            async def callback_select(i):
                if i.user == self.user:
                    selection = None
                    for select in selects:
                        if not select.values[0] is None:
                            selection = select.values[0]
                            break
                    self.view.disable_all_items()
                    embed = discord.Embed(
                        title=f"Setting changed by {self.user.name}",
                        description=f"The new suggestion channel is #{selection}",
                        color=discord.Color.random()
                    )
                    await i.message.edit(content=None, view=None, embed=embed)
                    await message.message.edit(view=self.view)

                    with open("settings.json", 'r') as file:
                        settings = json.load(file)
                    with open("settings.json", 'w') as file:
                        if str(interaction.guild.id) in settings.keys():
                            settings[str(interaction.guild.id)]["Suggestion Channel"] = str(
                                discord.utils.get(interaction.guild.channels, name=selection).id)
                        else:
                            settings[str(interaction.guild.id)] = self.default
                            settings[str(interaction.guild.id)]["Suggestion Channel"] = str(
                                discord.utils.get(interaction.guild.channels, name=selection).id)
                        json.dump(settings, file)
                else:
                    await i.response.send_message("You don't have permission to do that!", ephemeral=True)

            for select in selects:
                select.callback = callback_select
                view.add_item(select)
            await message.edit_original_response(view=view)
        else:
            await interaction.response.send_message("You don't have permission to do that!", ephemeral=True)


@bot.slash_command(name="settings", description="Change some settings.")
async def settings(ctx):
    if ctx.user.guild_permissions.administrator:
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
            view.add_item(settingsButton(0, str(index), defaultSettingsList, i, ctx.user))
        await message.edit_original_response(view=view)  # Edit view into message
    else:
        await ctx.respond("You need administrator privileges to access this.", ephemeral=True)


@bot.slash_command(name="purge",
                   description="Purge messages! Note: Old messages may not be purged.")
async def purge(ctx, limit: discord.Option(int)):
    if ctx.user.guild_permissions.manage_messages:
        await ctx.channel.purge(limit=limit)
        await ctx.respond(f"Purged {limit} messages by {ctx.user.name}")
    else:
        await ctx.respond(
            f"You do not have permission to purge messages. You need to have permission to manage messages.",
            ephemeral=True)


@bot.slash_command(name="randombobross", description="Random bob ross video")
async def randombobross(ctx):
    channel_url = feedparser.parse(
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCxcnsr1R5Ge_fbTu5ajt8DQ")  # Get all the videos from bob ross from XML request
    video = choice(
        channel_url.entries)  # https://www.reddit.com/r/Python/comments/ccbswi/i_wrote_a_small_script_that_opens_a_random_video/
    # The above comment is what I used to generate a random link
    embed = discord.Embed(
        title="Random Bob Ross",
        description=video.link,
        color=discord.Color.random()
    )

    await ctx.respond(video.link)
    await ctx.channel.send(embed=embed)


@bot.slash_command(name="randomvideofromchannel",
                   description="Get a random video from a channel!")
async def randomvideofromchannel(ctx, url: discord.Option(str, description="Use a link to the channel!")):
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    data = json.loads(re.search(r"var ytInitialData = ({.*});", str(soup.prettify())).group(
        1))  # https://www.youtube.com/watch?v=KcPimbou-kI
    channelUrl = str(data['header']['c4TabbedHeaderRenderer']['channelId'])
    channelName = str(data['header']['c4TabbedHeaderRenderer']['title'])
    channel_url = feedparser.parse(
        f"https://www.youtube.com/feeds/videos.xml?channel_id={channelUrl}")  # Get all the videos from bob ross from XML request
    video = choice(
        channel_url.entries)
    # The above comment is what I used to generate a random link
    embed = discord.Embed(
        title=f"Random video from {channelName}!",
        description=video.link,
        color=discord.Color.random()
    )

    await ctx.respond(video.link)
    await ctx.channel.send(embed=embed)


@randomvideofromchannel.error
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    await ctx.respond(f"I couldn't complete that request. Check perms, or change link. \n > ||ERROR: {error} ||",
                      ephemeral=True)


@bot.slash_command(name="doaflip", description="It says what it does...")
async def doaflip(ctx):
    embed = discord.Embed(
        title="You asked, I answered.",
        colour=discord.Colour.random()
    )
    await ctx.respond(embed=embed, file=discord.File("Doaflip.gif"))


@bot.user_command(name="Account Creation Date")
async def account_creation_date(ctx, member: discord.Member):
    await ctx.respond(f"{member.name}'s account was created on {member.created_at}")


@bot.slash_command(name="flip", description="Flip a coin!")
async def flip(ctx):
    randomNum = random.randint(0, 1)
    if randomNum == 0:
        results = "Heads!"
    else:
        results = "Tails!"
    embed = discord.Embed(
        title="Flip a coin!",
        colour=discord.Colour.random(),
        description=f"Results! \n {results}"
    )
    await ctx.respond(embed=embed)


@bot.slash_command(name="dog", description="Random dog picture")
async def dog(ctx):
    dogList = []
    breedTypeList = ["samoyed", "rottweiler", "golden", "pug", "schnauzer", "husky", "bernese", "hound", "terrier"]
    notWorkingList = ["https://images.dog.ceo/breeds/golden/caps.jpg", ")", "o"]
    for breed in breedTypeList:
        dogList.append(requests.get(f"https://dog.ceo/api/breed/{breed}/images").json()["message"])
    breedList = dogList[random.randint(0, len(dogList) - 1)]
    image = breedList[random.randint(0, len(breedList) - 1)]
    while (image in notWorkingList) or (not image.startswith("htt")):
        image = breedList[random.randint(0, len(breedList) - 1)]
    print(image)
    for item in image.split("/"):
        if item in breedTypeList:
            breed = item
    embed = discord.Embed(
        title="Random dog picture",
        colour=discord.Colour.random(),
        description=f"[Cool dog image!]({image}) \n The dog is of the {breed} breed.",
    )
    embed.set_image(url=image)

    await ctx.respond(embed=embed)


bot.run("MTA0NDMyMDUwNjk0MzM3NzQzOQ.GKrhD8.P2ggiWUov9lY9DHv6Gxc4scuyUtC6UeAIH09q8")
