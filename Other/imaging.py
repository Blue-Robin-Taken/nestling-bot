import discord
from discord.ext import commands
import PIL
from PIL import Image
import io
import os
import chardet


class imaging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    command_group = discord.SlashCommandGroup(name="imaging")
    hide_command_group = command_group.create_subgroup(name="hide")

    @hide_command_group.command(name="darkmode", description="Hides image for dark mode users")
    async def hide_darkmode(self, ctx,
                            attachment: discord.Option(discord.Attachment, required=True, description="Image to hide")):
        try:
            # await ctx.defer()
            embed = discord.Embed(
                title="Dark Mode",
                description="This image will be hidden for dark mode users",
                color=discord.Color.dark_blue()
            )
            temp = io.BytesIO()
            await attachment.save(temp)
            img = Image.open(
                temp).convert(
                'RGBA')  # https://stackoverflow.com/questions/24996518/what-size-to-specify-to-pil-image-frombytes
            imgdata = img.getdata()
            # grayscale
            grayscale = []
            for x in imgdata:
                Y = int(x[0] * 0.299) + int(x[1] * 0.587) + int(x[
                                                                    2] * 0.114)  # Helpful website: https://www.dynamsoft.com/blog/insights/image-processing/image-processing-101-color-space-conversion/
                Y = 255 - Y  # create inverse
                grayscale.append((Y, Y, Y))

            imgReturn = []
            for x in range(len(imgdata)):
                imgReturn.append((49,51,56, grayscale[x][0]))
            img.putdata(imgReturn)
            with io.BytesIO() as output:
                img.save(output, format="PNG")
                output.seek(0)
                await ctx.respond(file=discord.File(output, filename="darkmode.png"))

            # https://stackoverflow.com/questions/33101935/convert-pil-image-to-byte-array
            # https://www.youtube.com/watch?v=3PJE4PKdpxY
        except PIL.UnidentifiedImageError:
            await ctx.respond("This is not a valid image!", ephemeral=True)