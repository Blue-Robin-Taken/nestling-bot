import discord
from discord.ui import View, Button
from discord.ext import commands
import twentyfortyeight
import random


class TwentyFortyEightButton(Button):
    def __init__(self, row, emoji, game, user, color):
        super().__init__(style=discord.ButtonStyle.blurple, emoji=emoji, row=row)
        self.game = game
        self.user = user
        self.color = color

    async def callback(self, interaction):
        if self.user == interaction.user:
            await interaction.response.defer()
            if self.emoji.name == "▶":
                await self.game.Right()
            elif self.emoji.name == "◀":
                await self.game.Left()
            elif self.emoji.name == "🔼":
                await self.game.Up()
            elif self.emoji.name == "🔽":
                await self.game.Down()
            embed = discord.Embed(
                title="2048",
                description=twentyfortyeight.DecryptBoard(self.game.boardList),
                colour=discord.Colour.random()
            )
            embed.set_author(name=self.user, icon_url=self.user.avatar.url)
            embed.set_footer(text=f"Score: {self.game.score}")
            await interaction.message.edit(
                embed=embed)

        else:
            await interaction.response.send_message("This is not your game!", ephemeral=True)


class twentyfortyeightcommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="2048", description="Play 2048 on Discord!")
    async def twentyfortyeightcommand(self, ctx):
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
        view = View(timeout=300)
        view.add_item(TwentyFortyEightButton(0, "🔼", game, ctx.user, False))
        view.add_item(TwentyFortyEightButton(0, "🔽", game, ctx.user, False))
        view.add_item(TwentyFortyEightButton(0, "◀", game, ctx.user, False))
        view.add_item(TwentyFortyEightButton(0, "▶", game, ctx.user, False))

        await message.edit_original_response(view=view)


class eightball(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="eightball", description="Fun 8ball command!")
    async def eightball(self, ctx, question: discord.Option(str, description="Ask me anything!")):
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
