import discord
from discord.ext import commands
from PIL import ImageColor
from enum import Enum
import time
import datetime
import pymongo
import calendar
import os

client = pymongo.MongoClient(
    f"mongodb+srv://BlueRobin:{os.getenv('MONGOPASS')}@nestling-bot-settings.8n1wpmw.mongodb.net/?retryWrites=true&w=majority")
db = client.polls


class ExpireTime(Enum):
    One_Minute = 60


class Polls(commands.Cog):  # Polls is the class for creating polls
    def __init__(self, bot):
        self.bot = bot

        @bot.listen()
        async def on_raw_reaction_add(payload):
            message_id = payload.message_id
            guild = db.messages.find_one({
                '_id': message_id})  # guild is misleading (I'm too lazy to change the name). It's really the message found from the database
            if guild is not None:
                if guild[
                    'RemovalDate'].isoformat() < datetime.datetime.now().utcnow().isoformat():  # https://stackoverflow.com/questions/9433851/converting-utc-time-string-to-datetime-object
                    db.messages.delete_one(guild)
                    print('deleted one')
                    return
                channel = self.bot.get_guild(payload.channel_id)
                if channel is None:
                    channel = await self.bot.fetch_channel(payload.channel_id)
                message = bot.get_message(message_id)
                if message is None:
                    message = await channel.fetch_message(message_id)
                embed = message.embeds[0]
                value1 = discord.utils.get(message.reactions, emoji="🔽").count - 1
                value2 = discord.utils.get(message.reactions, emoji="🔼").count - 1
                bar = ""
                try:
                    percent1 = (value1 / (value1 + value2)) * 10
                    percent2 = (value2 / (value1 + value2)) * 10
                    bar = f"Upvotes {int(percent2 * 10)}%" + ("🟩" * int(percent2)) + (
                            int(percent1) * "🟥") + f" Downvotes {int(percent1 * 10)}%"  # https://chat.openai.com/share/7684565a-1f29-4c54-9d2f-502e051aef19
                except ZeroDivisionError:
                    print('ZeroDivision')
                    pass
                print('updated poll')
                embed.set_footer(text=bar)
                await message.edit(embed=embed)

    @staticmethod
    def hex_to_rgb(h):  # https://stackoverflow.com/questions/29643352/converting-hex-to-rgb-value-in-python
        return ImageColor.getcolor(h, "RGB")

    @commands.slash_command(name="simple_poll", description="Create a simple poll with two buttons")
    @discord.option('title', type=str)
    @discord.option('channel', type=discord.TextChannel, channel_types=[discord.ChannelType.text,
                                                                        discord.ChannelType.news,
                                                                        discord.ChannelType.news_thread,
                                                                        discord.ChannelType.public_thread,
                                                                        discord.ChannelType.private_thread])
    async def simple_poll(self, ctx, title, channel,
                          minutes: discord.Option(int, required=True, min_value=0, max_value=60),
                          hours: discord.Option(int, required=False, min_value=0, max_value=12) = 0,
                          days: discord.Option(int, required=False, min_value=0, max_value=120) = 0,
                          description: discord.Option(str, required=False) = "",
                          img: discord.Option(discord.Attachment, required=False) = None,
                          r: discord.Option(int, max_value=250, min_value=0, required=False) = None,
                          g: discord.Option(int, max_value=250, min_value=0, required=False) = None,
                          b: discord.Option(int, max_value=250, min_value=0, required=False) = None,
                          hex_color: discord.Option(str, required=False) = None):
        if ctx.user.guild_permissions.manage_guild:
            if description is None:
                description = ""
            await ctx.respond("Sending poll", ephemeral=True)
            color = discord.Color.random()
            if hex_color is not None:
                color = self.hex_to_rgb(hex_color)
                color = discord.Colour.from_rgb(color[0], color[1], color[2])
            elif (r is not None) and (g is not None) and (b is not None):
                color = discord.Colour.from_rgb(r, g, b)

            expiry_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes, hours=hours, days=days)
            embed = discord.Embed(
                title=title,
                description=description.replace("\\n", "\n") + f"\n \n Poll Expires: {'<t:' + str(calendar.timegm(expiry_time.timetuple())) + '>'}",
                # https://www.geeksforgeeks.org/convert-python-datetime-to-epoch/
                color=color
            )
            embed.set_footer(text="Upvotes 0% ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ Downvotes 0%")
            if img is not None:
                embed.set_image(url=img.url)

            m = await channel.send(embed=embed)  # m is the message that is sent
            await m.add_reaction("🔼")
            await m.add_reaction("🔽")
            db.messages.insert_one(
                {"_id": m.id, 'RemovalDate': expiry_time})
        else:
            await ctx.respond("You don't have the manage guild permissions", ephemeral=True)
