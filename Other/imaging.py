import discord
from discord.ext import commands
import PIL
from PIL import Image
from PIL import ImageDraw
from PIL import ImageColor
import io
import re
import random
from enum import Enum
import colorsys
import math


class imaging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def check_image_size(attachment):
        if attachment.size / 1000 > 500:
            return False
        else:
            return True

    @staticmethod
    def check_hex(color_hex):
        if color_hex is not None:
            match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$',
                              color_hex)  # https://stackoverflow.com/questions/30241375/python-how-to-check-if-string-is-a-hex-color-code/30241753#30241753
            if not match:
                return False
            else:
                return True

    @staticmethod
    def hex_to_rgb(h):  # https://stackoverflow.com/questions/29643352/converting-hex-to-rgb-value-in-python
        return ImageColor.getcolor(h, "RGB")

    command_group = discord.SlashCommandGroup(name="imaging")

    class emojis(Enum):
        blue = "🟦"
        green = "🟩"
        orange = "🟧"
        purple = "🟪"
        yellow = "🟨"
        red = "🟥"
        white = "⬜"
        black = "⬛"
        brown = "🟫"

    @staticmethod
    async def closest_color(rgb,
                      COLORS):  # https://stackoverflow.com/questions/54242194/python-find-the-closest-color-to-a-color-from-giving-list-of-colors
        r, g, b = rgb
        color_diffs = []
        for color in COLORS:
            cr, cg, cb = color
            color_diff = math.sqrt((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2)
            color_diffs.append((color_diff, color))
        return min(color_diffs)[1]

    @command_group.command(name='emoji-art', description="Create ascii art from image")
    async def emoji_art(self, ctx,
                        attachment: discord.Option(discord.Attachment, required=True, description="Image to use"),
                        size: discord.Option(int, required=True, description="Choose the output size! (keeps ratio)", max_value=600, min_value=1),
                        spaces: discord.Option(bool, required=False, description="If you want spaces between each character") = False,
                        ascii_true: discord.Option(bool, required=False, description="No color. Just ascii characters") = False):
        await ctx.defer()
        try:
            if not self.check_image_size(attachment):
                return await ctx.respond(
                    "Image too big. If you want image compression added, make a suggestion in the main server `/botinfo`",
                    ephemeral=True)

            temp = io.BytesIO()
            await attachment.save(temp)

            img = Image.open(
                temp).convert(
                'RGBA')  # https://stackoverflow.com/questions/24996518/what-size-to-specify-to-pil-image-frombytes
            r = size
            size_ = r, r
            if img.width > img.height:
                size_ = int(r), int((img.height / img.width) * r)
            if img.width > img.width:
                size_ = int((img.width / img.height) * r), int(r),

            img.thumbnail(size_, Image.Resampling.LANCZOS)
            imgdata = img.getdata()
            colors_list = {
                self.hex_to_rgb("#55acee"): "🟦",
                self.hex_to_rgb("#78b159"): "🟩",
                self.hex_to_rgb("#f4900c"): "🟧",
                self.hex_to_rgb("#aa8ed6"): "🟪",
                self.hex_to_rgb("#fdcb58"): "🟨",
                self.hex_to_rgb("#dd2e44"): "🟥",
                self.hex_to_rgb("#e6e7e8"): "⬜",
                self.hex_to_rgb("#31373d"): "⬛",
                self.hex_to_rgb("#c1694f"): "🟫",
            }
            # colors_list = {
            #     self.hex_to_rgb("#55acee"): ":blue_square:",
            #     self.hex_to_rgb("#78b159"): ":green_square:",
            #     self.hex_to_rgb("#f4900c"): ":orange_square:",
            #     self.hex_to_rgb("#aa8ed6"): ":purple_square:",
            #     self.hex_to_rgb("#fdcb58"): ":yellow_square:",
            #     self.hex_to_rgb("#dd2e44"): ":red_square:",
            #     self.hex_to_rgb("#e6e7e8"): ":white_large_square:",
            #     self.hex_to_rgb("#31373d"): ":black_large_square:",
            #     self.hex_to_rgb("#c1694f"): ":brown_square:",
            # }
            if ascii_true:
                colors_list = {
                    self.hex_to_rgb("#55acee"): "/",
                    self.hex_to_rgb("#78b159"): "%",
                    self.hex_to_rgb("#f4900c"): "@",
                    self.hex_to_rgb("#aa8ed6"): "$",
                    self.hex_to_rgb("#fdcb58"): ">",
                    self.hex_to_rgb("#dd2e44"): "<",
                    self.hex_to_rgb("#e6e7e8"): "*",
                    self.hex_to_rgb("#31373d"): " ",
                    self.hex_to_rgb("#c1694f"): "#",
                }

            # https://stackoverflow.com/questions/1847092/given-an-rgb-value-what-would-be-the-best-way-to-find-the-closest-match-in-the-d
            closest_colors = []
            closest_color = None
            for x in imgdata:
                closest_color = await self.closest_color(x[0:3], list(colors_list.keys()))
                closest_colors.append(closest_color)
            return_list = [colors_list[x] for x in closest_colors]  # get all emojis from their respective RGB values
            t = 0
            for x in range(len(return_list)):  # add newlines
                if spaces:
                    return_list.append('  ')
                if x % int(img.width) == 0:
                    return_list.insert(x + t, '\n')
                    t += 1

            with open('test.txt', 'w', encoding='utf-8', errors='replace') as f:
                f.write(''.join(return_list).strip())

            # end_list = []
            # return_list_sub = []
            # return_list_sub_sub = []
            # for i in return_list:
            #     if i == 'A':
            #         if return_list_sub:
            #             return_list_sub.append(return_list_sub_sub)
            #         return_list_sub_sub = []
            #     return_list_sub.append(i)
            # return_list_sub.append(return_list_sub_sub)
            # for line in return_list_sub:
            #     for x in range(len(line)):
            #         if x % step == 0:
            #             end_list.append(line[x])
            #     end_list.append('\n')
            # print("".join(end_list))
            # embed = discord.Embed(
            #     title='image',
            #     description="".join(return_list)
            # )
            with io.StringIO() as output:
                output.write(''.join(return_list))
                output.seek(0)
                await ctx.respond(
                    file=discord.File(output, filename="lol.txt"))  # Send the final product into discord
            # await ctx.respond(embed="".join(return_list))

        except PIL.UnidentifiedImageError as err:
            return await ctx.respond(
                "Image is not a valid image.",
                ephemeral=True)

    @command_group.command(name="hide", description="Hides image in certain color")
    async def hide(self, ctx,
                   attachment: discord.Option(discord.Attachment, required=True, description="Image to hide"),
                   color_hex: discord.Option(str, required=False, description="Color to hide"),
                   light_mode: discord.Option(bool, required=False, description="Invisible to light mode users")):

        try:
            if not self.check_image_size(attachment):
                return await ctx.respond(
                    "Image too big. If you want image compression added, make a suggestion in the main server `/botinfo`",
                    ephemeral=True)
            await ctx.defer()
            if color_hex is not None:
                match = self.check_hex(color_hex)
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
                grayscale.append((Y, Y, Y))  # append to list

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
                await ctx.respond(
                    file=discord.File(output, filename="darkmode.png"))  # Send the final product into discord

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
                return await ctx.respond(
                    "Image too big. If you want image compression added, make a suggestion in the main server `/botinfo`",
                    ephemeral=True)
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
        Analogous = "Analogous"

    @command_group.command(name="color_palette_generator",
                           description="Generates color palette")  # https://www.canva.com/colors/color-wheel/
    async def color_palette(self, ctx, amount: discord.Option(int, required=True,
                                                              description="Amount of colors to generate (might be dups)",
                                                              max_value=100, min_value=0),
                            palette_type: discord.Option(palette_types, required=True,
                                                         description="Type of color palette to generate",
                                                         ),
                            starter_color: discord.Option(str, required=False, description="Color to start with"),
                            rotate_value: discord.Option(int, required=False, description="Rotate colors for Analogous",
                                                         max_value=100, min_value=1) = 100,
                            min_sat: discord.Option(int, required=False, description="Minimum saturation for Analogous",
                                                    min_value=0, max_value=100) = 100,
                            min_brightness: discord.Option(int, required=False,
                                                           description="Minimum brightness for Analogous", min_value=0,
                                                           max_value=100) = 100):
        multi = 30
        e = 1
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        if starter_color is not None:
            if not self.check_hex(starter_color):
                return await ctx.respond("Invalid color", ephemeral=True)
            color = PIL.ImageColor.getcolor(starter_color, "RGB")
        if palette_type == imaging.palette_types.Monochromatic:

            colors = [
                (color[0] + (i * (360 / amount)), color[1] + (i * (360 / amount)), color[2] + (i * (360 / amount)))
                for i in range(amount)]
        elif palette_type == imaging.palette_types.Complementary:
            e = 2
            other_colors = [
                (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                for i in range(amount)]
            colors = [(abs(other_colors[i][0] + (i * (360 / amount) - 255)),
                       abs(other_colors[i][1] + (i * (360 / amount) - 255)),
                       abs(other_colors[i][2] + (i * (360 / amount) - 255)))
                      for i in range(amount)]

            colors.extend(other_colors)  # https://www.quora.com/How-do-you-find-an-RGB-complementary-color
        elif palette_type == imaging.palette_types.Analogous:
            HSV = colorsys.rgb_to_hsv(color[0] / 100, max(color[1] / 1000, round(min_sat / 1000)),
                                      max(color[2] / 100, round(min_brightness / 100)))
            print(HSV, color, round(min_brightness / 100))
            print(rotate_value, colorsys.hsv_to_rgb(HSV[0], HSV[1], HSV[2]))
            colors = [
                colorsys.hsv_to_rgb(abs(HSV[0] * ((rotate_value / 100) * i) * 10), abs(HSV[1] * 10), abs(HSV[2] * 10))
                for i in range(amount)]
            print(colors)
        # elif palette_type == imaging.palette_types.Analogous_Complementary:  # https://stackoverflow.com/questions/14095849/calculating-the-analogous-color-with-python
        #     other_colors = [
        #
        #     ]

        image = PIL.Image.new('RGB', (multi * amount * e, multi * e))
        draw = ImageDraw.Draw(image)
        for x in range(len(colors)):
            shape = [(0 + x * multi, 0), (image.width - (x * multi) + (x * multi), image.height)]
            draw.rectangle(shape, fill=(''.join('#%02x%02x%02x' % (
                abs(min(int(round(colors[x][0])), 255)), abs(min(int(round(colors[x][1])), 255)),
                abs(min(int(round(colors[x][2])), 255))))))
        with io.BytesIO() as output:
            image.save(output, format="PNG")
            print(colors)
            print('#%02x%02x%02x' % (abs(min(int(round(colors[i][0])), 255)), abs(min(int(round(colors[i][1])), 255)),
                                     abs(min(int(round(colors[i][2])), 255))) for i in range(len(colors)))
            embed = discord.Embed(
                title="Color Palette Generator",
                color=discord.Color.random(),
                description=f"Here is your color palette:\n\n{''.join(['#%02x%02x%02x' % (abs(min(int(round(colors[i][0])), 255)), abs(min(int(round(colors[i][1])), 255)), abs(min(int(round(colors[i][2])), 255))) + 'newline' for i in range(len(colors))])}".replace(
                    'newline', '\n'),
            )
            output.seek(0)
            await ctx.respond(embed=embed, file=discord.File(output, filename="color_palette.png"))
