import discord
from discord.ui import View, Select, Button
from discord.ext import commands
import json
import pymongo
import os

testing_servers = [1038227549198753862, 1044711937956651089, 821083375728853043]

client = pymongo.MongoClient(
    f"mongodb+srv://BlueRobin:{os.getenv('MONGOPASS')}@nestling-bot-settings.8n1wpmw.mongodb.net/?retryWrites=true&w=majority")
db = client.Fun


# noinspection PyUnresolvedReferences
class Stars(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def give_stars(self, ctx, user: discord.Member, amount: discord.Option(int, "How many stars do you want to give?", required=False, default=1, min_value=1, max_value=10)):
        if ctx.author.guild_permissions.administrator:
            coll = db.Starcount
            await ctx.respond(f"{user.mention} got {amount} star(s)! 🌟")
            try:
                coll.insert_one({"_id": {"guild": ctx.guild.id, "user": user.id}, "amount": amount})
            except pymongo.errors.DuplicateKeyError:
                coll.update_one({"_id": {"guild": ctx.guild.id, "user": user.id}}, {"$inc": {"amount": amount}})
        else:
            await ctx.respond("You don't have permission to do that.", ephemeral=True)

    @commands.slash_command(name="stars", description="See all stars")
    async def stars(self, ctx):
        coll = db.Starcount
        users = coll.find({})
        end_str = ""
        for user in users:
            if user["_id"]["guild"] == ctx.guild.id:
                end_str += f"Member: {ctx.guild.get_member(user['_id']['user'])} has {user['amount']} ⭐(s)\n"
        embed = discord.Embed(
            title="Stars",
            description=end_str,
            color=discord.Color.random()
        )
        if not end_str:
            embed = discord.Embed(
                title="This server doesn't have any 🌟.",
                color=discord.Color.random()
            )

        await ctx.respond(embed=embed)

    @commands.slash_command(name="unstar", description="Unstar a user.")
    async def unstar(self, ctx, user: discord.Option(discord.Member),
                     amount: discord.Option(int, min_value=1, default=1, max_value=10)):
        if user.guild_permissions.administrator:
            coll = db.Starcount
            try:
                coll.update_one({"_id": {"guild": user.guild.id, "user": user.id}}, {"$inc": {"amount": -amount}})
                if coll.find_one({"_id": {"guild": user.guild.id, "user": user.id}})["amount"] <= 0:
                    coll.delete_one({"_id": {"guild": user.guild.id, "user": user.id}})
                embed = discord.Embed(
                    title="Removed warn",
                    description=f"Removed star(s) for {user.mention} \n Removed {amount} star(s)",
                    color=discord.Color.random()
                )
            except TypeError:
                embed = discord.Embed(
                    title="This server doesn't have any stars.",
                    color=discord.Color.random()
                )

            await ctx.respond(embed=embed)
        else:
            await ctx.respond("You don't have permission to do that!", ephemeral=True)