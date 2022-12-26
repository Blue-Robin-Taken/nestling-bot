import discord
import requests
from discord.ui import Button, View, Select
import feedparser
import json
import random
from random import choice
from bs4 import BeautifulSoup
import re
from asgiref.sync import sync_to_async

# Bot cogs
import moderation
from Fun import games

bot = discord.Bot()
testing_servers = [1038227549198753862, 1044711937956651089, 821083375728853043]


# testing_servers = [1044711937956651089]

@bot.event
async def on_connect():
    bot.add_cog(moderation.warncommand(bot))
    bot.add_cog(moderation.warnscommand(bot))
    bot.add_cog(moderation.ban(bot))
    bot.add_cog(moderation.bans(bot))
    bot.add_cog(games.twentyfortyeightcommand(bot))
    bot.add_cog(games.eightball(bot))
    print("Connected!")


@bot.event
async def on_ready():
    print('ready')


@bot.slash_command(name='ping', description='Test if the bot is online!')
async def ping(ctx):
    await ctx.respond('Pong!')


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
        await message.add_reaction("⬆")
        await message.add_reaction("⬇")
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


class settingsButton(Button):
    def __init__(self, row, label, default, key, user, message):
        super().__init__(style=discord.ButtonStyle.blurple, label=label, row=row)
        self.default = default
        self.key = key
        self.user = user
        self.message = message

    async def callback(self, interaction):
        await interaction.response.defer()
        if interaction.user == self.user:
            message = await interaction.channel.send(self.key)
            categories = interaction.guild.categories
            options_list = []
            selects = []
            index = 0

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
            selects.append(Select(options=options_list))
            view = View()

            async def callback_select(i):
                await i.response.defer()
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
                    await self.message.edit_original_response(view=None)

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
            await message.edit(view=view)
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
            view.add_item(settingsButton(0, str(index), defaultSettingsList, i, ctx.user, message))
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
    request = await sync_to_async(requests.get)(url)
    soup = await sync_to_async(BeautifulSoup)(request.content, "html.parser")
    soup_pretty = await sync_to_async(soup.prettify)()
    re_search = await sync_to_async(re.search)(r"var ytInitialData = ({.*});", str(soup_pretty))
    data = await sync_to_async(json.loads)(await sync_to_async(re_search.group)(
        1))  # https://www.youtube.com/watch?v=KcPimbou-kI
    channelUrl = str(data['header']['c4TabbedHeaderRenderer']['channelId'])
    channelName = str(data['header']['c4TabbedHeaderRenderer']['title'])
    channel_url = await sync_to_async(feedparser.parse)(
        f"https://www.youtube.com/feeds/videos.xml?channel_id={channelUrl}")  # Get all the videos from bob ross from XML request
    video = await sync_to_async(choice)(
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
    await ctx.defer()
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
    await ctx.channel.send(embed=embed)
    await ctx.respond("Sent!")


@bot.slash_command(name="dog", description="Random dog picture")
async def dog(ctx):
    await ctx.defer()
    dogList = []
    breedTypeList = ["samoyed", "rottweiler", "golden", "pug", "schnauzer", "husky", "hound", "terrier", "mountain"]
    notWorkingList = ["https://images.dog.ceo/breeds/golden/caps.jpg", ")", "o"]
    for breed in breedTypeList:
        dogList.append(requests.get(f"https://dog.ceo/api/breed/{breed}/images").json()["message"])
    breedList = dogList[random.randint(0, len(dogList) - 1)]
    image = breedList[random.randint(0, len(breedList) - 1)]
    while (image in notWorkingList) or (not image.startswith("htt")):
        image = breedList[random.randint(0, len(breedList) - 1)]
        print(image, breedList)
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
    await ctx.channel.send(embed=embed)
    await ctx.respond("Sent!")


@bot.slash_command(name="bible", description="Put in a bible verse!")
async def bible(ctx, passage: discord.Option(str, description="Choose a passage or verse!")):
    api = requests.get(f"https://bible-api.com/{passage}?translation=kjv&verse_numbers=true").json()
    end_text = ""
    SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    try:
        for verse in api["verses"]:
            end_text += str(verse["verse"]).translate(SUP) + verse["text"]
        reference = api["reference"]
        embed = discord.Embed(
            title=f"Bible verse: {reference} KJV",
            colour=discord.Colour.random(),
            description=end_text
        )
        embed.set_author(name="Sent by: " + ctx.author.name)
    except KeyError:
        await ctx.respond(
            "Invalid request. If you think this is a mistake, please contact us in the bot's discord server.",
            ephemeral=True)
    try:
        await ctx.respond(embed=embed)
    except discord.errors.HTTPException:
        await ctx.respond(
            "Sorry, this passage is too long to print. The max length is 4096 characters. OR, there is an unknown error. If you think this is a mistake, please contact us in the bot's discord server.",
            ephemeral=True)


@bot.slash_command(name="invite",
                   description="Get the link to invite the bot to your server!")
async def invite(ctx):
    embed = discord.Embed(
        title="Invite the bot!",
        colour=discord.Colour.random(),
        description=f"Thanks!",
        url="https://discord.com/api/oauth2/authorize?client_id=1044320506943377439&permissions=3843929668855&scope=bot")
    embed.set_image(url=bot.user.avatar.url)
    await ctx.defer()
    await ctx.channel.send(embed=embed)


@bot.slash_command(name="bung", description="bung...")
async def bung(ctx):
    text = """
```
BUNGBUNGBUNGBUNG        BUNG        BUNG    BUNGBUNG            BUNG    BUNGBUNGBUNG
BUNGBUNGBUNGBUNG        BUNG        BUNG    BUNG BUNG           BUNG    BUNG
BUNG            BUNG    BUNG        BUNG    BUNG   BUNG         BUNG    BUNG
BUNG            BUNG    BUNG        BUNG    BUNG      BUNG      BUNG    BUNG    BUNG
BUNGBUNGBUNGBUNG        BUNG        BUNG    BUNG        BUNG    BUNG    BUNG        BUNG
BUNG            BUNG    BUNG        BUNG    BUNG          BUNG  BUNG    BUNG        BUNG
BUNG            BUNG    BUNG        BUNG    BUNG            BUNGBUNG    BUNG        BUNG
BUNGBUNGBUNGBUNG            BUNGBUNG        BUNG                BUNG    BUNGBUNGBUNGBUNG
```
    
    """
    await ctx.respond(text)


@bot.slash_command(name="info", description="Get bot info!")
async def info(ctx):
    amount = 0
    for i in bot.guilds:
        amount += 1
        print(i, i.member_count)
    embed = discord.Embed(
        description=f"I'm in {amount} servers!",
        color=discord.Color.random()
    )
    await ctx.respond(embed=embed)


bot.run("MTA0NDMyMDUwNjk0MzM3NzQzOQ.GKrhD8.P2ggiWUov9lY9DHv6Gxc4scuyUtC6UeAIH09q8")
