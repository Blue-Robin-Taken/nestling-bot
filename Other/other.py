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
        for i in self.bot.guilds:
            amount += 1
        embed = discord.Embed(
            title="Bot Info",
            description=f"I'm in {amount} servers! \n I also have a support server! [Join here!](https://discord.gg/m4j6eEmSQA) \n I have a documentation page: [here](https://nestlingbot.gitbook.io/nestling-bot-documentation/) \n My ping is: **{round(self.bot.latency * 1000, 1)}** ms",
            color=discord.Color.random()
        )
        await ctx.respond(embed=embed)


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
                title = "Hymn not found!",
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
