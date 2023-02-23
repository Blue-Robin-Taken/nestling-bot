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
        uuid = self.api.get_uuid(name)
        profile = self.api.get_profile(uuid)
        if not uuid:

            if not self.api.get_username(name):
                await ctx.respond("User not found")
                return
            else:
                uuid = name
                profile = self.api.get_profile(uuid)
        embed = discord.Embed(
            title=profile.name,
            description=f"The UUID of the user is `{uuid}`\nTheir nameMC page is [here](https://namemc.com/profile/{name}.1)",
            color=discord.Color.random(),
        )
        embed.set_footer(text="The user's avatar")
        embed.set_image(url=profile.skin_url)
        await ctx.respond(embed=embed)
