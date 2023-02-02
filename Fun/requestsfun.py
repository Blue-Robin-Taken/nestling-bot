import discord
from discord.ui import View, Button
from discord.ext import commands
from discord.commands import SlashCommandGroup
import requests
import random
import math


class testYoutube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.key = "AIzaSyC0QBEb_cSWCqOO8rbPG6t7edN-sFugslQ"

    # @commands.slash_command(name="randomvideofromchanneltest")
    # async def randomvideofromchanneltest(self, ctx, url: str):
    #     url = f"https://www.googleapis.com/youtube/v3/search?key={self.key}&channelId={}&part=snippet,id&order=date&maxResults=10000"
    #     response = requests.get(url)

    @commands.slash_command(name="randombobross")
    async def randombobross(self, ctx):
        url = f"https://www.googleapis.com/youtube/v3/search?key={self.key}&channelId=UCxcnsr1R5Ge_fbTu5ajt8DQ&part=snippet,id&order=date&maxResults=10000&type=video"
        response = requests.get(url)
        data = response.json()
        data_again = random.choice(data['items'])['id']
        send_url = "ERROR"
        try:
            send_url = "https://www.youtube.com/watch?v=" + data_again['videoId']
        except KeyError:
            print(data_again)

        await ctx.respond(send_url)
