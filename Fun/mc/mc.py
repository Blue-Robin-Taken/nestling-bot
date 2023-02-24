import discord
from discord.ui import View, Button
from discord.ext import commands
from discord.commands import SlashCommandGroup
import requests
import random
import math
import json
from bs4 import BeautifulSoup
from mojang import API
from datetime import datetime


class mc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = API()

    minecraft = SlashCommandGroup("minecraft", "mc related commands")
    users_minecraft = minecraft.create_subgroup("users", "Users related commands")

    @users_minecraft.command(name="get_user", description="Get a random user")
    async def get_user(self, ctx, name: str):
        request_json = requests.get(f"https://api.ashcon.app/mojang/v2/user/{name}").json()
        if "error" in request_json.keys():
            ctx.respond("Sorry, that user doesn't exist.")
            return
        uuid = request_json["uuid"]

        embed = discord.Embed(
            title=request_json["username"],
            description=f"The UUID of the user is `{uuid}`\nTheir account was created at: {request_json['created_at']}\nTheir nameMC page is [here](https://namemc.com/profile/{request_json['username']}.1)",
            color=discord.Color.random(),
        )

        embed.set_footer(text="The user's avatar")
        embed.set_image(url=request_json['textures']['skin']['url'])
        await ctx.respond(embed=embed)
