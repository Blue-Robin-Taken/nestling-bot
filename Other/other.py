import discord
from discord.ext import commands
import random
import json
import os
import math


class botinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="botinfo", description="Get bot info!")
    async def botinfo(self, ctx):
        amount = 0
        bot_channels = 0
        members = 0
        for i in self.bot.guilds:
            amount += 1
            bot_channels += len(i.channels)
            members += i.member_count
        embed = discord.Embed(
            title="Bot Info",
            description=f"I'm in {amount} servers! \n I'm in {bot_channels} channels! \n There are {members} members that can use my commands!\n I also have a support server! [Join here!](https://discord.gg/m4j6eEmSQA) \n I have a documentation page: [here](https://nestlingbot.gitbook.io/nestling-bot-documentation/) \n My ping is: **{round(self.bot.latency * 1000, 1)}** ms",
            color=discord.Color.random()
        )
        await ctx.respond(embed=embed)

    @commands.slash_command(name="documentation", description="Get the link to the documentation")
    async def documentation(self, ctx):
        embed = discord.Embed(title="Documentation", color=discord.Color.random(),
                              description="https://nestlingbot.gitbook.io/")
        await ctx.respond(embed=embed)


class reset_server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 300, commands.BucketType.guild)
    @commands.slash_command(name="reset-server",
                            description="Only usable by the server owner, this resets the server after a raid")
    async def reset_server(self, ctx):
        guild_temp = {"announce": ['Announcements'], "general": ['general']}
        if ctx.author == ctx.guild.owner:
            for role in ctx.guild.roles:  # remove roles
                try:
                    await role.delete()
                except discord.errors.HTTPException as e:
                    pass
            owner_role = await ctx.guild.create_role(name="Owner", color=discord.Color.red())
            await ctx.guild.owner.add_roles(owner_role)
            role = await ctx.guild.create_role(name='Member', color=discord.Color.green())
            for member in ctx.guild.members:  # give members a role
                await member.add_roles(role)  # add role

            print(ctx.guild.channels)
            for channel in ctx.guild.channels:
                try:
                    await channel.delete()  # delete channel
                except discord.errors.HTTPException as e:
                    pass # ignore

            for channel_group in guild_temp.keys():
                group = await ctx.guild.create_category(name=channel_group, position=0)
                await group.set_permissions(role, read_messages=True,
                                            send_messages=False)  # https://docs.pycord.dev/en/stable/api/models.html#discord.CategoryChannel.set_permissions
                for channel in guild_temp[channel_group]:
                    channel_ = await group.create_text_channel(name=channel)
                    if channel == "announce":
                        await channel_.edit(type=discord.ChannelType.news)

        else:
            await ctx.respond("You are not the owner of this server", ephemeral=True)

    @reset_server.error
    async def error(self, e):
        print(await e.channel.send('command on cooldown'))


class vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="vote", description="Vote for me!")
    async def vote(self, ctx):
        embed = discord.Embed(
            title="Thanks for voting!",
            color=discord.Color.random(),
            description=f"[Vote here!](https://top.gg/bot/1044320506943377439/vote) Thanks! \n Also join my support server! [Join here!](https://discord.gg/m4j6eEmSQA)")

        await ctx.respond(embed=embed)


class random_hymn_redbook(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="random_hymn_redbook", description="Get a random hymn from the redbook!")
    async def random_hymn_redbook(self, ctx):
        song = random.choice(os.listdir(os.path.relpath("Other/Song Lyrics")))
        with open(os.path.abspath("Other/Song Lyrics/" + song), "r", encoding="utf-8") as f:
            title = song.replace(".txt", "")
            content = f.read()
        embed = discord.Embed(
            title=title,
            description=content,
            color=discord.Color.random()
        )

        await ctx.respond(embed=embed)


class redbook(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="hymn_redbook", description="Get a hymn from the redbook!")
    async def random_hymn_redbook(self, ctx, number: int):
        song = None
        for i in os.listdir(os.path.relpath("Other/Song Lyrics")):
            if i.startswith("#" + str(number) + " "):
                song = i
        if song is None:
            embed = discord.Embed(
                title="Hymn not found!",
                description="No song found! If you believe this is a mistake, please ask in our support server. [Here!](https://discord.gg/m4j6eEmSQA)",
                color=discord.Color.random()
            )
            await ctx.respond(embed=embed)
            return
        with open(os.path.abspath("Other/Song Lyrics/" + song), "r", encoding="utf-8") as f:
            title = song.replace(".txt", "")
            content = f.read()
        embed = discord.Embed(
            title=title,
            description=content,
            color=discord.Color.random()
        )

        await ctx.respond(embed=embed)
