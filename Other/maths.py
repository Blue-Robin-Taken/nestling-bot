import discord
from discord.ui import View, Button
from discord.ext import commands
import random
import math


class quadratic_formula(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="quadratic_equation",
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


class standard_to_slope(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="standard_to_slope", description="Converts standard form to slope form (graphs)",
                            guild_ids=[1038227549198753862, 1044711937956651089, 821083375728853043])
    async def standard_to_slope(self, ctx, a: int, b: int, c: int):
        steps = []
        steps.append(f"{b}y = {a}x + ({c}) \n")
        steps.append(f"y = ({a}x + ({c})) / {b} \n")
        steps.append(f"y = ({a}x) / {b} + ({c}) / {b} \n")
        steps.append(f"y = {a / b}x + ({c / b})")
        embed = discord.Embed(color=discord.Color.random(), title="Standard to Slope",
                              description="```" + "".join(steps) + "```")
        await ctx.respond(embed=embed)
