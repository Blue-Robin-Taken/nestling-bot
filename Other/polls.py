import re
import discord
from discord.ext import commands


class Polls(commands.Cog):  # Polls is the class for creating polls
    def __init__(self, bot):
        self.bot = bot

    class simplePollView(discord.ui.View):
        @discord.ui.button(label="Upvote", style=discord.ButtonStyle.green)
        async def callback(self, button, interaction, emoji="🔼"):
            await interaction.response.send_message("Upvoted.", ephemeral=True, )

        @discord.ui.button(label="Downvote", style=discord.ButtonStyle.red)
        async def callback(self, button, interaction):
            await interaction.response.send_message("Upvoted.", ephemeral=True)

    @commands.slash_command(name="simple_poll", description="Create a simple poll with two buttons")
    async def simple_poll(self, ctx, title: str, img: discord.Attachment, hex_color:str, channel: discord.Option(discord.TextChannel,
                                                                                                  channel_types=[
                                                                                                      discord.ChannelType.text,
                                                                                                      discord.ChannelType.news,
                                                                                                      discord.ChannelType.public_thread])
                          , description: str = ""):
        await ctx.respond("Sending poll", ephemeral=True)
        embed = discord.Embed(
            title=title,
            description=description,
        )
        embed.set_image(url=img.url)
        await channel.send("testing", view=self.simplePollView())
