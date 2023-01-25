import discord
from discord.ext import commands


class bungcommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="bung", description="bung...")
    async def bung(self, ctx):
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


class syllablescommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vowels = ["a", "e", "i", "o", "u"]

    @commands.slash_command(name='syllables', description="Count the syllables")
    async def syllables(self, ctx, text: str):
        text = text.lower().split("")
        amount = 0
        for i in text:
            if i in self.vowels:
                amount += 1
        embed = discord.Embed(title="Syllables Count", color=discord.Color.random(), description=f"{amount} syllables")
        ctx.respond(embed=embed)
