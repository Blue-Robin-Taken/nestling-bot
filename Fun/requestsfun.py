import discord
from discord.ui import View, Button
from discord.ext import commands
from discord.commands import SlashCommandGroup
import requests
import random
import math
import json
import os


class testYoutube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.key = os.getenv('YTToken')

    @staticmethod
    async def randomvideoerr(ctx):
        await ctx.respond(
            f"I couldn't complete that request. Check perms, or change link.",
            ephemeral=True)

    @commands.slash_command(name="randomvideofromchannel")
    async def randomvideofromchannel(self, ctx, url: str):
        try:
            if not url.split('/')[2] == 'www.youtube.com':
                await self.randomvideoerr(ctx)
                return
            if len(url.split('/')) == 0:
                await self.randomvideoerr(ctx)
                return
        except IndexError:
            await self.randomvideoerr(ctx)
            return

        tabs = ['featured', 'community', 'playlists', 'videos', 'channels', 'about', 'items']
        try:
            channel_id = url.split('/')[4]
            if channel_id in tabs:
                channel_name = url.split('/')[3].replace('@', '')
                search_url = f"https://www.googleapis.com/youtube/v3/search?part=id%2Csnippet&q={channel_name}&type=channel&key={self.key}"
                response = requests.get(search_url)
                try:
                    channel_id = response.json()['items'][0]['id']['channelId']
                except KeyError:
                    print(response.json())
        except IndexError:
            channel_name = url.split('/')[3].replace('@', '')
            search_url = f"https://www.googleapis.com/youtube/v3/search?part=id%2Csnippet&q={channel_name}&type=channel&key={self.key}"
            response = requests.get(search_url)
            channel_id = response.json()['items'][0]['id']['channelId']

        url = f"https://www.googleapis.com/youtube/v3/search?key={self.key}&channelId={channel_id}&part=snippet,id&order=date&maxResults=100&type=video"
        response = requests.get(url)
        data = response.json()
        data_again = random.choice(data['items'])['id']
        send_url = "ERROR"
        try:
            send_url = "https://www.youtube.com/watch?v=" + data_again['videoId']
        except KeyError:
            print(data_again)

        await ctx.respond(send_url)

    @randomvideofromchannel.error
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        await ctx.respond(f"I couldn't complete that request. Check perms, or change link. \n > ||ERROR: {error} ||",
                          ephemeral=True)

    @commands.slash_command(name="randombobross")
    async def randombobross(self, ctx):
        with open("Fun/data/bobross.json", "r") as f:
            data = json.load(f)
        data_again = random.choice(data['items'])['id']
        send_url = "ERROR"
        try:
            send_url = "https://www.youtube.com/watch?v=" + data_again['videoId']
        except KeyError:
            print(data_again)

        await ctx.respond(send_url)
