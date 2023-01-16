import discord
from discord.ext import commands
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
            description=f"I'm in {amount} servers! \n I also have a support server! [Join here!](https://discord.gg/m4j6eEmSQA) \n My ping is: **{round(self.bot.latency * 1000, 1)}** ms",
            color=discord.Color.random()
        )
        await ctx.respond(embed=embed)
