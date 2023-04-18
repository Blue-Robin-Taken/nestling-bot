import discord
from discord.ext import commands
import PIL
from PIL import Image
import io
import re


class imaging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    command_group = discord.SlashCommandGroup(name="imaging")

    @command_group.command(name="hide", description="Hides image in certain color")
    async def hide(self, ctx,
                   attachment: discord.Option(discord.Attachment, required=True, description="Image to hide"),
                   color_hex: discord.Option(str, required=False, description="Color to hide"), light_mode: discord.Option(bool, required=False, description="Invisible to light mode users")):

        try:
            await ctx.defer()
            if color_hex is not None:
                match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$',
                                  color_hex)  # https://stackoverflow.com/questions/30241375/python-how-to-check-if-string-is-a-hex-color-code/30241753#30241753
                if not match:
                    return await ctx.respond("Invalid color")
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
                if color_hex is not None:
                    rgb = PIL.ImageColor.getcolor(color_hex, "RGB") # https://stackoverflow.com/questions/29643352/converting-hex-to-rgb-value-in-python
                    imgReturn.append((rgb[0], rgb[1], rgb[2], grayscale[x][0]))
                elif light_mode is not None:
                    rgb = PIL.ImageColor.getcolor("#FEFFFE", "RGB") # https://stackoverflow.com/questions/29643352/converting-hex-to-rgb-value-in-python
                    imgReturn.append((rgb[0], rgb[1], rgb[2], grayscale[x][0]))
                else:
                    imgReturn.append((49, 51, 56, grayscale[x][0]))
            img.putdata(imgReturn)
            with io.BytesIO() as output:
                img.save(output, format="PNG")
                output.seek(0)
                await ctx.respond(file=discord.File(output, filename="darkmode.png"))

            # https://stackoverflow.com/questions/33101935/convert-pil-image-to-byte-array
            # https://www.youtube.com/watch?v=3PJE4PKdpxY
        except PIL.UnidentifiedImageError:
            await ctx.respond("This is not a valid image!", ephemeral=True)
