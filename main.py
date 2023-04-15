import discord
import requests
from discord.ui import Button, View, Select
import json
import random
from asgiref.sync import sync_to_async
import pymongo
import enum

# Bot cogs
import moderation
from Fun import games
from Fun import randomgames
from Fun import requestsfun
from Fun import starsystem
from Fun.mc import mc
from Other import other
from Other import maths
from Other import settings
from Other import reaction_roles
import re

bot = discord.Bot(intents=discord.Intents.all())
testing_servers = [1038227549198753862, 1044711937956651089, 821083375728853043]

# testing_servers = [1044711937956651089]
async_thread_sense = False
cogs = (moderation.warning, moderation.ban, moderation.bans,
        games.twentyfortyeightcommand, games.eightball, randomgames.bungcommand, other.botinfo, other.vote,
        maths.algebra, other.random_hymn_redbook, other.redbook, settings.Settings,
        maths.geometry, maths.other, requestsfun.testYoutube, randomgames.emoji, mc.mc, starsystem.Stars,
        reaction_roles.ReactionRoles, games.rockpaperscissors)

client = pymongo.MongoClient(
    "mongodb+srv://BlueRobin:ZaJleEpNhBUxqMDK@nestling-bot-settings.8n1wpmw.mongodb.net/?retryWrites=true&w=majority")
db = client.settings


def load_cogs():
    for cog in cogs:
        bot.add_cog(cog(bot))
        print(cog)

    print("Loaded cogs")


@bot.event
async def on_connect():
    try:
        await bot.sync_commands()
    except discord.HTTPException as e:
        print(e)
    print("Connected!")
    url = f"https://www.googleapis.com/youtube/v3/search?key=AIzaSyC0QBEb_cSWCqOO8rbPG6t7edN-sFugslQ&channelId=UCxcnsr1R5Ge_fbTu5ajt8DQ&part=snippet,id&order=date&maxResults=100&type=video"
    data = requests.get(url).json()
    with open("Fun/data/bobross.json", "w") as f:
        json.dump(data, f, indent=4)
        f.close()
    print('Dumped data')


@bot.slash_command(name="channel_type", description="Get a channel type")
async def channel_type(ctx, channel):
    try:

        channel = await bot.fetch_channel(int(channel))
        await ctx.respond(channel.type)
    except AttributeError as e:
        await ctx.respond(e)


@bot.event
async def on_ready():
    bot.add_view(SuggestView())
    bot.add_view(reaction_roles.ReactionRoles.ReactionView([]))
    print('ready')


@bot.event
async def on_member_join(member):
    label = "Auto Role"
    coll = getattr(db, f"{label}")
    if coll.find_one({"_id": member.guild.id}) is not None:
        role = member.guild.get_role(coll.find_one({"_id": member.guild.id})['role'])
        await member.add_roles(role)
        print(str(role) + " joined")


@bot.slash_command(name='ping', description='Test if the bot is online!')
async def ping(ctx):
    await ctx.respond('Pong! (Run /botinfo for ping)')


class SuggestView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(self.RejectButton())
        self.add_item(self.AcceptButton())

    class RejectButton(discord.ui.Button):
        def __init__(self):
            super().__init__(style=discord.ButtonStyle.blurple, emoji="❌", custom_id="reject")

        async def callback(self, interaction):
            embed = discord.Embed(
                color=discord.Color.red(),
                title=f"ERROR",
            )

            if interaction.user.guild_permissions.manage_guild:
                embed = discord.Embed(
                    color=discord.Color.red(),
                    title=f"Messaged Rejected!",
                    description=f"This message was rejected by {interaction.user.name}"
                )
                self.view.disable_all_items()
                await interaction.message.edit(view=self.view)
                await interaction.response.send_message(embed=embed, ephemeral=False)

            else:
                embed = discord.Embed(
                    color=discord.Color.red(),
                    title=f"You don't have the permissions to do that!",
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

    class AcceptButton(discord.ui.Button):
        def __init__(self):
            super().__init__(style=discord.ButtonStyle.blurple, emoji="✅", custom_id="accept")

        async def callback(self, interaction):
            embed = discord.Embed(
                color=discord.Color.red(),
                title=f"ERROR",
            )

            if interaction.user.guild_permissions.manage_guild:
                embed = discord.Embed(
                    color=discord.Color.green(),
                    title=f"Messaged Approved!",
                    description=f"This message was approved by {interaction.user.name}"
                )
                self.view.disable_all_items()
                await interaction.message.edit(view=self.view)
                await interaction.response.send_message(embed=embed, ephemeral=False)

            else:
                embed = discord.Embed(
                    color=discord.Color.red(),
                    title=f"You don't have the permissions to do that!",
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.slash_command(name="suggest",
                   description="Suggest something in the set suggestion channel!")
async def suggest(ctx, suggestion: discord.Option(str, description="Suggest anything!")):
    label = "Suggestion Channel"
    coll = getattr(db, f"{label}")
    if coll.find_one({"_id": ctx.guild.id}) is not None:
        channel = discord.utils.get(ctx.guild.text_channels, id=coll.find_one({"_id": ctx.guild.id})['channel'])
        embed = discord.Embed(
            color=discord.Color.red(),
            title=f"Suggestion by {ctx.author.name}",
            description=f"{suggestion}",
        )
        await ctx.respond("Sending message!", ephemeral=True)
        message = await channel.send(embed=embed)
        await message.add_reaction("⬆")
        await message.add_reaction("⬇")
        view = SuggestView()
        await message.edit(view=view)
    else:
        await ctx.respond("No suggestion channel set! Set one with /settings", ephemeral=True)


class AnnounceButton(Button):
    def __init__(self, row, emoji, channel, message, self_message, user):
        super().__init__(style=discord.ButtonStyle.blurple, emoji=emoji, row=row)
        self.channel = channel
        self.message = message
        self.message_self = self_message
        self.user = user

    async def callback(self, interaction):
        if interaction.user.id == self.user.id:
            self.view.disable_all_items()
            await self.message_self.edit(view=self.view)
            embed = None
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
                    description=f"```If you think this was a bug, please talk to the developer. (in the support server)```")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(f"You aren't the user who ran this command.", ephemeral=True)


@bot.slash_command(name="announce", description="Make server announcements!")
async def announce(ctx, channel: discord.Option(discord.TextChannel,
                                                channel_types=[discord.ChannelType.text, discord.ChannelType.news,
                                                               discord.ChannelType.news_thread,
                                                               discord.ChannelType.public_thread,
                                                               discord.ChannelType.private_thread,
                                                               discord.ChannelType.news],
                                                description="Copy the text channel in developer mode, or just use the # system."),

                   title: str, text: str,
                   color_r: discord.Option(int, required=False, max_value=255, min_value=0) = 0,
                   color_g: discord.Option(int, required=False, max_value=255, min_value=0) = 0,
                   color_b: discord.Option(int, required=False, max_value=255, min_value=0) = 0,
                   color_hex: discord.Option(str, required=False,
                                             description="If RGB is inputted and this is as well, this will be the output") = "#000000",
                   ):
    if not color_hex == "#000000":
        match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color_hex)
        if match:
            rgb = tuple(int(color_hex.lstrip('#')[i:i + 2], 16) for i in (
                0, 2, 4))  # https://stackoverflow.com/questions/29643352/converting-hex-to-rgb-value-in-python
            color_r = rgb[0]
            color_g = rgb[1]
            color_b = rgb[2]
    color = discord.Color.from_rgb(r=color_r, g=color_g, b=color_b)
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("You do not have the permissions to do that!")
        return
    newText = text.replace("\\n", "\n")
    embed_check = discord.Embed(
        color=color,
        title=title,
        description=newText
    )
    await ctx.respond(embed=embed_check)
    message = await ctx.channel.send("Is this correct?")
    view = View()
    view.add_item(AnnounceButton(0, "✅", channel, embed_check, message, ctx.author))
    view.add_item(AnnounceButton(0, "❌", channel, embed_check, message, ctx.author))
    await message.edit(view=view)


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


@bot.slash_command(name="largetest",
                   description="(Sorry, but only the owner of this bot can use this command (That's me))",
                   guild_ids=testing_servers)
async def largetest(ctx):
    if ctx.author.id == 497930397985013781:
        await ctx.respond("Lol you didn't set anything. ")
    else:
        await ctx.respond("Sorry, but only the owner of this bot can use this command (That's me!)")


@bot.slash_command(name="dog", description="Random dog picture")
async def dog(ctx):
    await ctx.defer()
    dogList = []
    breedList = None
    breedTypeList = ["samoyed", "rottweiler", "pug", "schnauzer", "husky", "hound", "terrier", "mountain"]
    notWorkingList = [")", "a", "b", "c", "d", "e", "f", "g", "h", "i",
                      "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "x", "y", "z"]
    for breed in breedTypeList:
        request = await sync_to_async(requests.get, False)(f"https://dog.ceo/api/breed/{breed}/images")
        dogList.append(request.json()["message"])
    try:
        breedList = dogList[random.randint(0, len(dogList) - 1)]
        image = breedList[random.randint(0, len(breedList) - 1)]
    except ValueError:
        await ctx.channel.send(f"ERROR")
        print(dogList)
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
        description=f"[Cool dog image!]({image}) \n The dog is of the {image.split('/')[4]} breed.",
    )
    embed.set_image(url=image)
    await ctx.channel.send(embed=embed)
    await ctx.respond("Sent!")


@bot.slash_command(name="bible", description="Put in a bible verse!")
async def bible(ctx, passage: discord.Option(str, description="Choose a passage or verse!")):
    api = requests.get(f"https://bible-api.com/{passage}?translation=kjv&verse_numbers=true").json()
    end_text = ""
    SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    embed = None
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
        if embed is not None:
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
    await ctx.respond(embed=embed)


load_cogs()  # Load all cogs into the bot
bot.run(
    "MTA0NDMyMDUwNjk0MzM3NzQzOQ.GKrhD8.P2ggiWUov9lY9DHv6Gxc4scuyUtC6UeAIH09q8")  # Run the bot and connect to discord
