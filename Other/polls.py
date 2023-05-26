import discord
from discord.ext import commands
from PIL import ImageColor


class simplePollView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(self.upvote())
        self.add_item((self.downvote()))

    class upvote(discord.ui.Button):
        def __init__(self):
            super().__init__(label="Upvote", style=discord.ButtonStyle.green)

        async def callback(self, interaction):
            await interaction.response.send_message("Upvoted.", ephemeral=True, )

    class downvote(discord.ui.Button):
        def __init__(self):
            super().__init__(label="Downvote", style=discord.ButtonStyle.red)

        async def callback(self, interaction):
            await interaction.response.send_message("Downvoted.", ephemeral=True, )


class Polls(commands.Cog):  # Polls is the class for creating polls
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def hex_to_rgb(h):  # https://stackoverflow.com/questions/29643352/converting-hex-to-rgb-value-in-python
        return ImageColor.getcolor(h, "RGB")

    @commands.slash_command(name="simple_poll", description="Create a simple poll with two buttons")
    async def simple_poll(self, ctx, title: str, channel: discord.Option(discord.TextChannel,
                                                                         channel_types=[
                                                                             discord.ChannelType.text,
                                                                             discord.ChannelType.news,
                                                                             discord.ChannelType.public_thread]),
                          description: discord.Option(str, required=False),
                          img: discord.Option(discord.Attachment, required=False),
                          r: discord.Option(int, max_value=250, min_value=0, required=False),
                          g: discord.Option(int, max_value=250, min_value=0, required=False),
                          b: discord.Option(int, max_value=250, min_value=0, required=False),
                          hex_color: discord.Option(str, required=False)):
        if description is None:
            description = ""
        await ctx.respond("Sending poll", ephemeral=True)
        color = discord.Color.random()
        if hex_color is not None:
            color = self.hex_to_rgb(hex_color)
        elif (r is not None) and (g is not None) and (b is not None):
            color = discord.Colour.from_rgb(r, g, b)
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        if img is not None:
            embed.set_image(url=img.url)

        await channel.send(embed=embed, view=simplePollView())

        await ctx.channel.send("Poll sent!")
