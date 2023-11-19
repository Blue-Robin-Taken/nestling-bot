import discord
import requests
from discord.ui import Button, View, Select
import json
import random
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
from Other import encrypt
from Other import imaging
from Other import polls
from Other import reddit
import re
import datetime
from enum import Enum
import functools  # https://stackoverflow.com/questions/53368203/passing-args-kwargs-to-run-in-executor
import os
import cloudinary  # image storage
from cloudinary import uploader

intents = discord.Intents.default()
# noinspection PyDunderSlots,PyUnresolvedReferences
intents.messages = True
# noinspection PyDunderSlots,PyUnresolvedReferences
intents.message_content = True
# noinspection PyDunderSlots,PyUnresolvedReferences
intents.members = True
bot = discord.Bot(intents=intents)
testing_servers = [1038227549198753862, 1044711937956651089, 821083375728853043]

# testing_servers = [1044711937956651089]
async_thread_sense = False
cogs = (moderation.warning, moderation.ban, moderation.bans,
        games.twentyfortyeightcommand, games.eightball, randomgames.bungcommand, other.botinfo, other.vote,
        maths.algebra, other.random_hymn_redbook, other.redbook, settings.Settings,
        maths.geometry, maths.other, requestsfun.testYoutube, randomgames.emoji, mc.mc, starsystem.Stars,
        reaction_roles.ReactionRoles, games.rockpaperscissors, encrypt.encryption, imaging.imaging, games.counting,
        polls.Polls, other.raid_protection, games.SnakeGame, games.DodgeKickBlockPunch, reddit.Memes)

client = pymongo.MongoClient(
    f"mongodb+srv://BlueRobin:{os.getenv('MONGOPASS')}@nestling-bot-settings.8n1wpmw.mongodb.net/?retryWrites=true&w=majority")
db = client.settings

# https://stackoverflow.com/questions/12201928/open-gives-filenotfounderror-ioerror-errno-2-no-such-file-or-directory

cloudinary.config(
    cloud_name="dxopzyxoi",
    api_key="594498119421517",
    api_secret=f"{os.getenv('CLOUD_IMAGE_STORAGE')}"
)


def load_cogs():
    for cog in cogs:
        bot.add_cog(cog(bot))
        print(cog)

    print("Loaded cogs")


@bot.listen()
async def on_connect():
    print("Connected!")
    url = f"https://www.googleapis.com/youtube/v3/search?key={str(os.getenv('YTTOKEN'))}&channelId=UCxcnsr1R5Ge_fbTu5ajt8DQ&part=snippet,id&order=date&maxResults=100&type=video"
    data = requests.get(url).json()
    with open("Fun/data/bobross.json", "w") as f:
        json.dump(data, f, indent=4)
        f.close()
    print('Dumped data')
    # await bot.sync_commands()


@bot.slash_command(name="channel_type", description="Get a channel type")
async def channel_type(ctx, channel):
    try:
        channel = await bot.fetch_channel(int(channel))
        await ctx.respond(channel.type)
    except (AttributeError, discord.errors.NotFound, ValueError, discord.errors.HTTPException) as e:
        await ctx.respond(e)


def clean_message_database():  # cleans the database of old polls
    coll = client.polls.messages
    for guild in coll.find({}):
        if guild[
            'RemovalDate'].isoformat() < datetime.datetime.now().utcnow().isoformat():  # https://stackoverflow.com/questions/9433851/converting-utc-time-string-to-datetime-object
            coll.delete_one(guild)


@bot.event
async def on_ready():
    bot.add_view(SuggestView())
    bot.add_view(reaction_roles.ReactionRoles.ReactionView([]))
    clean_message_database()
    print('cleaned database')
    print('ready')


# @bot.listen()
# async def on_message(m):
#     if m.guild.id ==

@bot.event
async def on_member_join(member):
    label = "Auto Role"
    coll = getattr(db, f"{label}")

    if coll.find_one({"_id": member.guild.id}) is not None:
        # try to get from the cache first
        role = member.guild.get_role(int(coll.find_one({"_id": member.guild.id})['role']))
        if role is not None:
            await member.add_roles(role)
            return

        # if it's not found in cache, make an API request
        role = discord.utils.get(await member.guild.fetch_roles(),
                                 id=int(coll.find_one({"_id": member.guild.id})['role']))
        await member.add_roles(role)
        print(str(role) + " joined")


@bot.slash_command(name='ping', description='Test if the bot is online!')
async def ping(ctx):
    await ctx.respond('Pong! (Run /botinfo for ping)')


@bot.slash_command(name="serverinfo", description="Get information about this server")
async def serverinfo(ctx):
    bot_count = 0
    members = 0
    for member in ctx.guild.members:
        if member.bot:
            bot_count += 1
        else:
            members += 1
    embed = discord.Embed(
        title=ctx.guild.name,
        color=discord.Color.random(),
    )
    embed.set_image(url=ctx.guild.icon.url)
    embed.add_field(  # server member amount
        name="Server Member Amount",
        value=f"Bots: {bot_count} \n Members: {members} \n",
        inline=False
    )
    embed.add_field(  # server channels amount
        name="Server Channels Count",
        value=f"Text Channels: {len(ctx.guild.text_channels)} \n Voice Channels: {len(ctx.guild.voice_channels)} \n Forum Channels: {len(ctx.guild.forum_channels)} \n Stage Channels: {len(ctx.guild.stage_channels)} \n Threads: {len(ctx.guild.threads)}",
        inline=False
    )
    embed.add_field(
        name="Server Role Count",
        value=f"Roles: {len(ctx.guild.roles)}",
        inline=False
    )
    await ctx.respond(embed=embed)


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
async def suggest(ctx, suggestion: discord.Option(str, description="Suggest anything!"),
                  image: discord.Option(discord.Attachment, required=False, description="Most image types supported")):
    label = "Suggestion Channel"
    coll = getattr(db, f"{label}")
    if coll.find_one({"_id": ctx.guild.id}) is not None:
        channel = discord.utils.get(ctx.guild.text_channels, id=coll.find_one({"_id": ctx.guild.id})['channel'])
        embed = discord.Embed(
            color=discord.Color.red(),
            title=f"Suggestion by {ctx.author.name}",
            description=f"{suggestion}",
        )

        if image is not None:
            url = uploader.upload(image.url)['url']
            embed.set_image(url=url)
            # embed.set_image(url=image.url)  <-- removed because discord deletes after a while

        await ctx.respond("Sending message!", ephemeral=True)
        try:
            message = await channel.send(embed=embed)
        except discord.errors.Forbidden:
            return ctx.channel.send("I am not authorized to create a suggestion. Please contact a server moderator.")
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
                try:
                    await self.channel.send(embed=self.message)
                except discord.errors.Forbidden:
                    return await interaction.response.send_message("I don't have permission to send.")
            elif self.emoji.name == "❌":
                embed = discord.Embed(
                    color=discord.Color.red(),
                    title=f"Announcement canceled!",
                    description=f"```If you think this was a bug, please talk to the developer. (in the support server)```")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(f"You aren't the user who ran this command.", ephemeral=True)


@bot.slash_command(name="announce",
                   description="Make server announcements! Use \\n in the message to create a new line!")
async def announce(ctx, channel: discord.Option(discord.TextChannel,
                                                channel_types=[discord.ChannelType.text, discord.ChannelType.news,
                                                               discord.ChannelType.news_thread,
                                                               discord.ChannelType.public_thread,
                                                               discord.ChannelType.private_thread],
                                                description="Copy the text channel in developer mode, or just use the # system."),

                   title: str, text: str,
                   author: discord.Option(str, required=False, description="The author of the announcement."),
                   attachment: discord.Option(discord.Attachment, required=False,
                                              description="The attachment of the announcement. Videos don't work."),
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
        description=newText,
    )
    if attachment is not None:
        url = uploader.upload(attachment.url)['url']
        embed_check.set_image(url=url)
        # embed_check.set_image(url=attachment.url)  <- doesn't work cuz discord bald
    if author is not None:
        embed_check.set_author(name=author)
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


# bellow variables generate list of breed options for dog command
dog_all_breeds = requests.get('https://dog.ceo/api/breeds/list/all').json()  # request json
dog_breed_general_types = list(dog_all_breeds['message'].keys())  # general breed types
breed_types = []  # initiate list
for dog_breed_ in dog_breed_general_types:  # loop through all breed types to see if there are subtypes & add either general or subtype
    if len(dog_all_breeds['message'][dog_breed_]) > 0:  # if it has subtype then add it
        for breed__ in dog_all_breeds['message'][dog_breed_]:  # breed_ is every sub breed
            breed_types.append(f"{dog_breed_}/{breed__}")  # add sub breed to end with / because of formatting
    else:  # else, append the general type
        breed_types.append(dog_breed_)
dog_breeds = discord.Option(str, autocomplete=discord.utils.basic_autocomplete(breed_types),
                            required=False)  # create options using autocomplete util


@bot.slash_command(name="dog", description="Random dog picture", )
async def dog(ctx, breed: dog_breeds):
    if breed is not None:
        if breed not in breed_types:
            return await ctx.respond('Breed does not exist', ephemeral=True)
        await ctx.defer()
        request = await bot.loop.run_in_executor(None, requests.get, f"https://dog.ceo/api/breed/{breed}/images/random")
        image = request.json()['message']
    else:
        request = await bot.loop.run_in_executor(None, requests.get, f"https://dog.ceo/api/breeds/image/random")
        image = request.json()['message']

    embed = discord.Embed(
        title="Random dog picture",
        colour=discord.Colour.random(),
        description=f"[Cool dog image!]({image})",
    )
    embed.set_image(url=image)
    await ctx.respond(embed=embed)

cat_all_breeds = requests.get('https://api.thecatapi.com/v1/breeds').json()  # request json
print(cat_all_breeds)
# cat_breed_general_types = [cat_breed for cat_breed in cat_all_breeds.keys()]  # general breed types


@bot.slash_command(name="cat", description="Random cat picture", )
async def cat(ctx, ):
    request = await bot.loop.run_in_executor(None, functools.partial(requests.get,
                                                                     f"https://api.thecatapi.com/v1/images/search",
                                                                     headers={'x-api-key': os.getenv('CATAPIKEY')}))
    image = request.json()[0]['url']
    print(image)
    embed = discord.Embed(
        title="Random cat picture",
        colour=discord.Colour.random(),
        description=f"[Cool cat image!]({image})",
    )
    embed.set_image(url=image)
    await ctx.respond(embed=embed)


@bot.slash_command(name="penguin", description="Random penguin picture", )
async def penguin(ctx, ):
    request = await bot.loop.run_in_executor(None, functools.partial(requests.get,
                                                                     f"https://penguin.sjsharivker.workers.dev/api"))
    image = request.json()['img']
    species = request.json()['species']
    embed = discord.Embed(
        title="Random penguin picture",
        colour=discord.Colour.random(),
        description=f"[Cool penguin image!]({image})",
    )
    embed.add_field(name="species", value=str(species))
    embed.add_field(name="API", value="[Github](https://github.com/code2cube/PenguinImageAPI)")
    embed.set_image(url=image)
    await ctx.respond(embed=embed)


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
bot.run(str(os.getenv('BOT_TOKEN_')))  # Run the bot and connect to discord
