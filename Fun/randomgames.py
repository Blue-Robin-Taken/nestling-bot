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


class emoji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='text_to_emoji', description="It says what it does")
    async def text_to_emoji(self, ctx, text: str):
        full_string = ""
        l = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
             'v', 'w', 'x', 'y', 'z']
        n = {
            "0": ":zero:",
            "1": ":one:",
            "2": ":two:",
            "3": ":three:",
            "4": ":four:",
            "5": ":five:",
            "6": ":six:",
            "7": ":seven:",
            "8": ":eight:",
            "9": ":nine:",
            "10": ":keycap_ten:",
            "?": ":question:",
            "!": ":exclamation:",
        }
        for letter in list(text):
            if letter.lower() in l:
                full_string += ":regional_indicator_" + letter.lower() + ": "
            elif letter in n:
                full_string += " " + n[letter] + " "
            else:
                full_string += letter
        embed = discord.Embed(title="Text to Emoji", color=discord.Color.random(), description=full_string + f'\n ```{full_string}```')
        await ctx.respond(embed=embed)
