import discord
from discord.ext import commands
import requests
import os


class Memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    reddit_token = str(os.getenv('REDDIT_TOKEN'))
    command_group = discord.SlashCommandGroup(name="reddit")

    def get_embed(self, subreddit):
        subreddit = f"https://www.reddit.com/r/{subreddit}/"  # https://github.com/Krystian93/CreepyJson/blob/master/index.js

        request = requests.get(subreddit + "random.json", headers={
            'User-agent': self.reddit_token})  # https://www.reddit.com/r/redditdev/comments/3qbll8/429_too_many_requests/
        data = request.json()[0]['data']['children'][0]['data']
        title = data['title']
        url = 'https://www.reddit.com' + data['permalink']

        image = None
        if 'url_overridden_by_dest' in data:
            image = data['url_overridden_by_dest']
        embed = discord.Embed(
            color=discord.Color.red(),
            description=data['selftext'],
            title=title,
            url=url,
        )
        embed.set_footer(text=f'Score: {data["score"]}')
        embed.set_author(name=data['author'], url=f"https://www.reddit.com/user/{data['author']}/")
        if image is not None:
            embed.set_image(url=image)
        return embed

    @command_group.command(name="programmermemes")
    async def programmerMemes(self, ctx):
        await ctx.defer()
        embed = self.get_embed("ProgrammerHumor")
        await ctx.respond(embed=embed)

    @command_group.command(name='random')
    async def random(self, ctx, name: str):
        await ctx.defer()
        try:
            embed = self.get_embed(name)
            await ctx.respond(embed=embed)
        except KeyError:
            await ctx.respond('Invalid subreddit or another error has occurred.', ephemeral=True)
