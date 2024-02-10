# import discord
# from discord.ext import commands
# import requests
# import os
# import time
# import hashlib


# class Memes(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         #  https://www.youtube.com/watch?v=FdjVoOf9HN4
#         self.authentication = auth.HTTPBasicAuth(
#             os.getenv("REDDIT_ID"),
#             os.getenv("REDDIT_PASS")
#         )
#         print(self.authentication)
#         self.user_tokens = {}
#         self.hashing_obj = hashlib.md5()
#
#     command_group = discord.SlashCommandGroup(name="reddit")

    # def refresh_token(self, user_id):
    #
    #     special_id = self.hashing_obj.
    #     res = requests.post("https://reddit.com/api/v1/access_token", headers={
    #         'User-Agent': "SparkedHost:NestlingBot 1.0 (by /u/Blue_Robin_Gaming)"}, auth=self.authentication,
    #                         data={
    #
    #                         })
    #     print(res.text)
    #     TOKEN = res.json()['access_token']
    #     self.user_tokens[f"{user_id}"] = {TOKEN, time.time()}
    #
    # def get_embed(self, subreddit):
    #
    #     subreddit = f"https://www.reddit.com/r/{subreddit}/"  # https://github.com/Krystian93/CreepyJson/blob/master/index.js
    #     if self.time_passed > 300:  # if 5 mins passed, refresh the token
    #         self.refresh_token()
    #     request = requests.get(subreddit + "random.json", headers={
    #         'User-Agent': "Nestling Bot 1.0 (u/BlueRobinTaken)", "Authorization": f"bearer {self.TOKEN}"},
    #                            auth=auth)  # https://www.reddit.com/r/redditdev/comments/3qbll8/429_too_many_requests/
    #     print(request.text)
    #     data = request.json()[0]['data']['children'][0]['data']
    #     title = data['title']
    #     url = 'https://www.reddit.com' + data['permalink']
    #
    #     image = None
    #     if 'url_overridden_by_dest' in data:
    #         image = data['url_overridden_by_dest']
    #     embed = discord.Embed(
    #         color=discord.Color.red(),
    #         description=data['selftext'],
    #         title=title,
    #         url=url,
    #     )
    #     embed.set_footer(text=f'Score: {data["score"]}')
    #     embed.set_author(name=data['author'], url=f"https://www.reddit.com/user/{data['author']}/")
    #     if image is not None:
    #         embed.set_image(url=image)
    #     return embed
    #
    # @command_group.command(name="programmermemes")
    # async def programmerMemes(self, ctx):
    #     await ctx.defer()
    #     embed = self.get_embed("ProgrammerHumor")
    #     await ctx.respond(embed=embed)
    #
    # @command_group.command(name='random')
    # async def random(self, ctx, name: str):
    #     await ctx.defer()
    #     try:
    #         embed = self.get_embed(name)
    #         await ctx.respond(embed=embed)
    #     except KeyError:
    #         await ctx.respond('Invalid subreddit or another error has occurred.', ephemeral=True)
