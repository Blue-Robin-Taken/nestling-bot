import discord
from discord.ext import commands
import PIL
from PIL import Image
from PIL import ImageDraw
import io
import re
import random
from enum import Enum


class imaging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def check_image_size(attachment):
        if attachment.size / 1000 > 500:
            return False
        else:
            return True

    command_group = discord.SlashCommandGroup(name="imaging")

    @command_group.command(name="hide", description="Hides image in certain color")
    async def hide(self, ctx,
                   attachment: discord.Option(discord.Attachment, required=True, description="Image to hide"),
                   color_hex: discord.Option(str, required=False, description="Color to hide"),
                   light_mode: discord.Option(bool, required=False, description="Invisible to light mode users")):

        try:
            if not self.check_image_size(attachment):
                return await ctx.respond("Image too big. If you want image compression added, make a suggestion in the main server `/botinfo`", ephemeral=True)
            await ctx.defer()
            if color_hex is not None:
                match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$',
                                  color_hex)  # https://stackoverflow.com/questions/30241375/python-how-to-check-if-string-is-a-hex-color-code/30241753#30241753
                if not match:
                    return await ctx.respond("Invalid color", ephemeral=True)
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
                    rgb = PIL.ImageColor.getcolor(color_hex,
                                                  "RGB")  # https://stackoverflow.com/questions/29643352/converting-hex-to-rgb-value-in-python
                    imgReturn.append((rgb[0], rgb[1], rgb[2], grayscale[x][0]))
                elif light_mode is not None:
                    rgb = PIL.ImageColor.getcolor("#FEFFFE",
                                                  "RGB")  # https://stackoverflow.com/questions/29643352/converting-hex-to-rgb-value-in-python
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

    @command_group.command(name="grayscale", description="Converts image to grayscale")
    async def grayscale(self, ctx,
                        attachment: discord.Option(discord.Attachment, required=True,
                                                   description="Convert image to grayscale"),
                        inverse: discord.Option(bool, required=False, description="Invert image grayscale")):
        try:
            if not self.check_image_size(attachment):
                return await ctx.respond("Image too big. If you want image compression added, make a suggestion in the main server `/botinfo`", ephemeral=True)
            await ctx.defer()
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
                if inverse:
                    Y = 255 - Y  # create inverse
                grayscale.append((Y, Y, Y))

            img.putdata(grayscale)
            with io.BytesIO() as output:
                img.save(output, format="PNG")
                output.seek(0)
                await ctx.respond(file=discord.File(output, filename="grayscale.png"))

        except PIL.UnidentifiedImageError:
            print(attachment.content_type)
            await ctx.respond("This is not a valid image!", ephemeral=True)

    class palette_types(Enum):
        Monochromatic = "Monochromatic"
        Complementary = "Complementary"

    @command_group.command(name="color_palette_generator", description="Generates color palette")
    async def color_palette(self, ctx, amount: discord.Option(int, required=True,
                                                              description="Amount of colors to generate (might be dups)",
                                                              max_value=100, min_value=0),
                            palette_type: discord.Option(palette_types, required=True,
                                                         description="Type of color palette to generate", )):
        multi = 30
        e = 1
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        if palette_type == imaging.palette_types.Monochromatic:
            colors = [
                (color[0] + (i * (360 / amount)), color[1] + (i * (360 / amount)), color[2] + (i * (360 / amount)))
                for i in range(amount)]
        elif palette_type == imaging.palette_types.Complementary:
            e = 2
            other_colors = [
                (color[0] + (i * (360 / amount)), color[1] + (i * (360 / amount)), color[2] + (i * (360 / amount)))
                for i in range(round(amount))]
            colors = [(abs(color[0] + (i * (360 / amount) - 255)), abs(color[1] + (i * (360 / amount) - 255)),
                       abs(color[2] + (i * (360 / amount) - 255)))
                      for i in range(amount)]

            colors.extend(other_colors)  # https://www.quora.com/How-do-you-find-an-RGB-complementary-color

        image = PIL.Image.new('RGB', (multi * amount * e, multi * e))
        draw = ImageDraw.Draw(image)
        for x in range(len(colors)):
            shape = [(0 + x * multi, 0), (image.width - (x * multi) + (x * multi), image.height)]
            draw.rectangle(shape, fill=(''.join('#%02x%02x%02x' % (
                min(int(round(colors[x][0])), 255), min(int(round(colors[x][1])), 255),
                min(int(round(colors[x][2])), 255)))))
        with io.BytesIO() as output:
            image.save(output, format="PNG")
            embed = discord.Embed(
                title="Color Palette Generator",
                color=discord.Color.random(),
                description=f"Here is your color palette:\n\n{''.join(['#%02x%02x%02x' % (min(int(round(i[0])), 255), min(int(round(i[1])), 255), min(int(round(i[2])), 255)) + 'newline' for i in colors])}".replace(
                    'newline', '\n'),
            )
            output.seek(0)
            await ctx.respond(embed=embed, file=discord.File(output, filename="color_palette.png"))
