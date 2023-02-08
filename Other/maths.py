import discord
from discord.ui import View, Button
from discord.ext import commands
from discord.commands import SlashCommandGroup
import random
import math
import plotly.express as px
import pandas as pd
import io


class other(commands.Cog):
    other = SlashCommandGroup("other", "Commands that are of the other")
    text_changing = other.create_subgroup("text_changing", "Changes the text of the inputted string")

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def get_super(
            x):  # Copied from geeks for geeks (Thanks!)  (https://www.geeksforgeeks.org/how-to-print-superscript-and-subscript-in-python/)
        normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=()"
        super_s = "ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾQᴿˢᵀᵁⱽᵂˣʸᶻᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖ۹ʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾"
        res = x.maketrans(''.join(normal), ''.join(super_s))
        return x.translate(res)

    @text_changing.command(name="superscript", description="Convert a number or text to superscript.")
    async def superscript(self, ctx, text: str):
        embed = discord.Embed(title="Superscript", color=discord.Color.random(), description=self.get_super(text))
        await ctx.respond(embed=embed)

    @staticmethod
    def get_sub(
            x):  # Copied from geeks for geeks (Thanks!)  (https://www.geeksforgeeks.org/how-to-print-superscript-and-subscript-in-python/)
        normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=()"
        sub_s = "ₐ₈CDₑբGₕᵢⱼₖₗₘₙₒₚQᵣₛₜᵤᵥwₓᵧZₐ♭꜀ᑯₑբ₉ₕᵢⱼₖₗₘₙₒₚ૧ᵣₛₜᵤᵥwₓᵧ₂₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎"
        res = x.maketrans(''.join(normal), ''.join(sub_s))
        return x.translate(res)

    @text_changing.command(name="subscript", description="Convert a number or text")
    async def subscript(self, ctx, text: str):
        embed = discord.Embed(title="Subscript", color=discord.Color.random(), description=self.get_sub(text))
        await ctx.respond(embed=embed)


# --- Algebra ---
class algebra(commands.Cog):
    algebra = SlashCommandGroup("algebra", "Algebra Commands")
    graphing = algebra.create_subgroup("graphing", "Graphing Commands")

    def __init__(self, bot):
        self.bot = bot

    @algebra.command(name="quadratic_equation",
                     description="Does the quadratic equation for you, instead of spending 5 mins with a calculator!")
    async def quadratic_equation(self, ctx, a: int, b: int, c: int):
        def quadratic_formula(a, b, c):
            discriminant = ((b) ** 2) - (4 * a * c)

            answer_fraction_1 = str(-b) + '+' + "Sqrt(" + str(discriminant) + ")" + "/" + str((2 * a))
            answer_fraction_2 = str(-b) + '-' + "Sqrt(" + str(discriminant) + ")" + "/" + str((2 * a))
            number_of_solutions = "error"
            try:
                answer_1 = ((-b) + math.sqrt(discriminant)) / (2 * a)
                answer_2 = ((-b) - math.sqrt(discriminant)) / (2 * a)
            except ValueError:
                if discriminant == 0:
                    number_of_solutions = 1
                elif discriminant + abs(discriminant) == 0:
                    number_of_solutions = 0
                elif discriminant + abs(discriminant) != 0:
                    number_of_solutions = 2
                return {"number_of_solutions": number_of_solutions, "discriminant": discriminant,
                        "answer_fraction_1": answer_fraction_1, "answer_fraction_2": answer_fraction_2,
                        "Math Domain Error": None}
            if discriminant == 0:
                number_of_solutions = 1
            elif discriminant + abs(discriminant) == 0:
                number_of_solutions = 0
            elif discriminant + abs(discriminant) != 0:
                number_of_solutions = 2
            return {"answer_1": answer_1, "answer_2": answer_2, "answer_fraction_1": answer_fraction_1,
                    "answer_fraction_2": answer_fraction_2, "number_of_solutions": number_of_solutions,
                    "discriminant": discriminant}

        quadratic_formula = quadratic_formula(int(a), int(b), int(c))

        if "Math Domain Error" in quadratic_formula:
            embed = discord.Embed(color=discord.Color.red(), title="Quadratic Equation", description=f"""Your input:
                            A: {a}
                            B: {b}
                            C: {c}

                            Number of solutions: {quadratic_formula["number_of_solutions"]}
                            Discriminant: {quadratic_formula["discriminant"]}
                            Answer fraction add: {quadratic_formula["answer_fraction_1"]}
                            Answer fraction subtract: {quadratic_formula["answer_fraction_2"]}
                              """)
        else:
            embed = discord.Embed(
                color=discord.Color.red(), title="Quadratic Equation", description=f"""Your input:
                              A: {a}
                              B: {b}
                              C: {c}

                              Number of solutions: {quadratic_formula["number_of_solutions"]}
                              Discriminant: {quadratic_formula["discriminant"]}
                              Answer fraction add: {quadratic_formula["answer_fraction_1"]}
                              Answer fraction subtract: {quadratic_formula["answer_fraction_2"]}
                              Answer add: {quadratic_formula["answer_1"]}
                              Answer subtract: {quadratic_formula["answer_2"]}""")

        embed.add_field(name="Quadratic equation formula:", value="**ax^2 + bx + c = 0**")
        await ctx.respond(embed=embed)

    @algebra.command(name="standard_to_slope", description="Converts standard form to slope form (graphs)")
    async def standard_to_slope(self, ctx, a: int, b: int, c: int):
        steps = [f"{a}x + {b}y = {c} \n",
                 f"{b}y = {-a}x + ({c}) \n",
                 f"y = ({-a}x + ({c})) / {b} \n",
                 f"y = ({-a}x / {b}) + ({c} / {b}) \n",
                 f"y = {-a / b}x + ({c / b})"]
        embed = discord.Embed(color=discord.Color.random(), title="Standard to Slope",
                              description="Steps\n```go\n" + "".join(steps) + "```"
                                          + f"""
                              Base equation 
                              `y = mx + b`
                              
                              Full equation 
                              `y = {-a / b}x + {c / b}`""".replace("    ", ""))
        await ctx.respond(embed=embed)

    @algebra.command(name="slope_to_standard", description="Converts slope form to standard form")
    async def slope_to_standard(self, ctx, m: int, b: int):
        steps = [f"y = {m}x + ({b})\n",
                 f"{-m}x + y = {b}\n"]
        embed = discord.Embed(color=discord.Color.random(), title="Slope to Standard",
                              description="Steps\n```go\n" + "".join(steps) + "```"
                                          + f"""
                              Base equation 
                              `ax + by = c`

                              Full equation 
                              `y = {-m}x + y = {b}`""".replace("    ", ""))
        await ctx.respond(embed=embed)

    @graphing.command(name="slope_graph",
                      description="Creates a slope graph out of slope intercept form.")
    async def slope_graph(self, ctx, m: int, b: int, length: discord.Option(int, default=100, max_value=500, min_value=0)):
        if length > 500:
            await ctx.respond(embed=discord.Embed(title="Error", description="Length must be less than 500."))
            return
        data_x = []
        data_y = []
        for i in range(length):
            data_x.append(i)
            data_y.append(m * i + b)
        df = pd.DataFrame(dict(
            x=data_x,
            y=data_y
        ))

        fig = px.line(df, x="x", y="y", title="Slope Graph")

        with io.BytesIO() as image_binary:  # https://stackoverflow.com/questions/63209888/send-pillow-image-on-discord-without-saving-the-image
            fig.write_image(image_binary, 'PNG')
            image_binary.seek(0)
            embed = discord.Embed(color=discord.Color.random(), title=f"Slope Graph",)
            await ctx.respond(embed=embed, file=discord.File(fp=image_binary, filename='image.png'))
            image_binary.close()


# --- Geometry ---


class geometry(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    geometry = SlashCommandGroup("geometry", "For most geometry related math equations. Good luck!")
    geometry_area = geometry.create_subgroup("area", "Get the area of almost any shape.")
    geometry_perimeter = geometry.create_subgroup("perimeter", "Get the perimeter of almost any shape.")
    geometry_surface_area = geometry.create_subgroup("surface_area", "Get the surface area of a shape.")

    # -- Area and Perimeter --
    @geometry_area.command(name="trapezoid_area", description="Calculate the area of a trapezoid",
                           guild_ids=[1038227549198753862, 1044711937956651089, 821083375728853043])
    async def trapezoid_area(self, ctx, b1: int, b2: int, height: int):
        embed = discord.Embed(color=discord.Color.random(), title="Trapezoid Area", description=f"""The area of the trapezoid is 
        ```go\n {.5 * ((b1 + b2) * height)}```
        Base equation: ½(b1+b2)h""")
        await ctx.respond(embed=embed)

    @geometry_area.command(name="triangle_area", description="Calculates the area of a triangle")
    async def triangle_area(self, ctx, base: int, height: int):
        embed = discord.Embed(color=discord.Color.random(), title="Triangle Area", description=f"""The area of the triangle is 
        ```go\n {base * height / 2}```
        Base equation: ½bh""")
        await ctx.respond(embed=embed)

    @geometry_area.command(name="rectangle_area", description="Calculates the area")
    async def rectangle_area(self, ctx, width: int, height: int):
        embed = discord.Embed(color=discord.Color.random(), title="Rectangle Area", description=f"""The area of the rectangle is 
        ```{width * height}```""")
        await ctx.respond(embed=embed)

    @geometry_area.command(name="square_area", description="Calculates the area of a square")
    async def square_area(self, ctx, side: int):
        embed = discord.Embed(color=discord.Color.random(), title="Square Area", description=f"""The area of the square is 
        ```{side * side}```""")
        await ctx.respond(embed=embed)

    @geometry_perimeter.command(name="rectangle_perimeter", description="Calculates the perimeter of a rectangle")
    async def rectangle_perimeter(self, ctx, width: int, height: int):
        embed = discord.Embed(color=discord.Color.random(), title="Rectangle Perimeter", description=f"""The perimeter of the rectangle is 
        ```{(width * 2) + (height * 2)}```
        
        Base equation 
        ```l * 2 + w * 2 = perimeter```""")
        await ctx.respond(embed=embed)

    @geometry_area.command(name="circumference", description="Calculates the circumference")
    async def circumference(self, ctx, radius: int):
        embed = discord.Embed(color=discord.Color.random(), title="Circumference", description=f"""
        The circumference of the circle is 
        ```{radius * 2 * math.pi}```
        
        Base equation 
        ``` 2πr² = circumference```""")
        await ctx.respond(embed=embed)

    # -- Surface Area --
    @geometry_surface_area.command(name="cube_area", description="Get the surface area of a cube.")
    async def cube_area(self, ctx, edge: int):
        embed = discord.Embed(
            color=discord.Color.random(),
            title="Cube Surface Area",
            description=f"""The surface area of the cube is \n ```go\n{6 * (edge ** 2)}``` \n \n Base Equation ```go\n6a²```"""
        )
        await ctx.respond(embed=embed)

    @geometry_surface_area.command(name="cylinder_area", description="Get the surface area of a cylinder.")
    async def cylinder_area(self, ctx, radius: int, height: int):
        embed = discord.Embed(
            color=discord.Color.random(),
            title="Cylinder Surface Area",
            description=f"""The surface area of the cylinder is \n ```go\n{2 * math.pi * radius * height + (2 * math.pi * (radius ** 2))}``` \n \n Base Equation ```go\n2πrh + 2πr²```""")
        await ctx.respond(embed=embed)

    @geometry_surface_area.command(name="cone_area", description="Get the surface area of a cone.")
    async def cone_area(self, ctx, radius: int, height: int):
        slant = math.sqrt((height ** 2) + (radius ** 2))
        embed = discord.Embed(
            color=discord.Color.random(),
            title="Cone Surface Area",
            description=f"""The slant height of the cone is ```go\n{slant}```\n The surface area of the cone is ```go\n{math.pi * (radius ** 2) + math.pi * radius * slant}``` \n \n Base Equation ```go\nπrl+πr2```""")
        await ctx.respond(embed=embed)

    @geometry_surface_area.command(name="sphere_area", description="Get the surface area of a sphere.")
    async def sphere_area(self, ctx, radius: int):
        embed = discord.Embed(
            color=discord.Color.random(),
            title="Sphere Surface Area",
            description=f"""The surface area of the sphere is \n ```go\n{4 * math.pi * (radius ** 2)}``` \n \n Base Equation ```go\n4πr²```""")
        await ctx.respond(embed=embed)
