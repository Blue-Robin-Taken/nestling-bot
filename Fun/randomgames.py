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
