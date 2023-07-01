import discord
from discord.ui import View, Button
from discord.ext import commands
import twentyfortyeight
import random
import snake
import pymongo
import os

client = pymongo.MongoClient(
    f"mongodb+srv://BlueRobin:{os.getenv('MongoPass')}@nestling-bot-settings.8n1wpmw.mongodb.net/?retryWrites=true&w=majority")


class TwentyFortyEightButton(Button):
    def __init__(self, row, emoji, game, user, color):
        super().__init__(style=discord.ButtonStyle.blurple, emoji=emoji, row=row)
        self.game = game
        self.user = user
        self.color = color

    async def callback(self, interaction):
        if self.user == interaction.user:
            await interaction.response.defer()
            if self.emoji.name == "▶":
                await self.game.Right()
            elif self.emoji.name == "◀":
                await self.game.Left()
            elif self.emoji.name == "🔼":
                await self.game.Up()
            elif self.emoji.name == "🔽":
                await self.game.Down()
            embed = discord.Embed(
                title="2048",
                description=twentyfortyeight.DecryptBoard(self.game.boardList),
                colour=discord.Colour.random()
            )
            embed.set_author(name=self.user, icon_url=self.user.avatar.url)
            embed.set_footer(text=f"Score: {self.game.score}")
            await interaction.message.edit(
                embed=embed)

        else:
            await interaction.response.send_message("This is not your game!", ephemeral=True)


class twentyfortyeightview(View):
    def __init__(self, user, game, m):
        super().__init__(timeout=500)
        self.message = m
        self.add_item(TwentyFortyEightButton(0, "🔼", game, user, False))
        self.add_item(TwentyFortyEightButton(0, "🔽", game, user, False))
        self.add_item(TwentyFortyEightButton(0, "◀", game, user, False))
        self.add_item(TwentyFortyEightButton(0, "▶", game, user, False))

    async def on_timeout(self):
        self.disable_all_items()
        await self.message.edit_original_response(view=self)
        await self.message.channel.send("Game timed out!")


class twentyfortyeightcommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="2048", description="Play 2048 on Discord!")
    async def twentyfortyeightcommand(self, ctx):
        game = twentyfortyeight.TwentyFortyEight(False)
        string = twentyfortyeight.DecryptBoard(game.boardList)
        embed = discord.Embed(
            title="2048",
            description=string,
            colour=discord.Colour.random()
        )
        embed.set_author(name=ctx.user, icon_url=ctx.user.avatar.url)
        embed.set_footer(text=f"Score: {game.score}")

        message = await ctx.respond(embed=embed)
        view = twentyfortyeightview(ctx.user, game, message)

        await message.edit_original_response(view=view)


class eightball(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="eightball", description="Fun 8ball command!")
    async def eightball(self, ctx, question: discord.Option(str, description="Ask me anything!")):
        random.seed(str(ctx.user.id) + question)
        responses = ["Maybe.", "I have no idea.", "I think so.", "Yes.", "Why would you ask that?", "No.", "Yes.",
                     "Probably.", "Funny.", "Who are you again?", "When is lunch?", "Yes 1+1 is two. So, yes.",
                     "Maybe go see a therapist.", "Lol.", "I wish.", "Imagine."]
        random_self = random.randint(0, len(responses) - 1)

        embed = discord.Embed(
            color=discord.Color.red(),
            title="Eightball",
            description=f"""
        **My answer**:
        {responses[random_self]}

        **You asked**:
        {str(question)}

        """
        )
        await ctx.respond(embed=embed)


class rockpaperscissors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class RPSView(discord.ui.View):
        class RPSButton(discord.ui.Button):
            def __init__(self, emoji, user):
                super().__init__(style=discord.ButtonStyle.blurple, emoji=emoji)
                self.user = user

            async def callback(self, interaction: discord.Interaction):
                if interaction.user.id == self.user.id:
                    i = random.randint(0, 2)
                    options = ["rock", "paper", "scissors"]
                    # 0 = rock
                    # 1 = paper
                    # 2 = scissors
                    conditionals = {
                        i == 0 and self.emoji.name == "✂": "lost",
                        i == 0 and self.emoji.name == "🪨": "draw",
                        i == 0 and self.emoji.name == "📃": "won",
                        i == 1 and self.emoji.name == "✂": "won",
                        i == 1 and self.emoji.name == "🪨": "lost",
                        i == 1 and self.emoji.name == "📃": "draw",
                        i == 2 and self.emoji.name == "✂": "draw",
                        i == 2 and self.emoji.name == "🪨": "won",
                        i == 2 and self.emoji.name == "📃": "lost",
                    }
                    condition = conditionals.get(True)

                    embed = discord.Embed(
                        color=discord.Color.random(),
                        title="Rock Paper Scissors",
                        description=f"I choose {options[i]}. You choose {self.emoji.name}."
                    )
                    if condition == "lost":
                        await interaction.response.send_message("You lost!", embed=embed)
                    if condition == "won":
                        await interaction.response.send_message("You won!", embed=embed)
                    if condition == "draw":
                        await interaction.response.send_message("It's a draw!", embed=embed)

                    self.view.disable_all_items()
                    await self.view.message.edit(view=self.view)
                else:
                    interaction.response.send_message("This is not your game!", ephemeral=True)

        def __init__(self, ctx):
            super().__init__()
            self.add_item(self.RPSButton("🪨", ctx.author))
            self.add_item(self.RPSButton("✂", ctx.author))
            self.add_item(self.RPSButton("📃", ctx.author))

    @commands.slash_command(name="rockpaperscissors", description="Play rock paper scissors")
    async def rockpaperscissors(self, ctx):

        embed = discord.Embed(
            color=discord.Color.random(),
            title="Rock Paper Scissors",
            description=f"Choose one!"
        )

        view = self.RPSView(ctx)
        await ctx.respond(embed=embed, view=view)


class counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = client.Fun
        self.coll = self.db.Count
        self.coll_users = self.db.Count_Users

        @bot.listen()
        async def on_message(message):
            try:
                coll = getattr(client.settings, "Counting Channel")
                channel_dict = coll.find_one(
                    {"_id": message.guild.id})  # return value of column for counting channel settings
                if channel_dict is not None:
                    if message.channel.id == channel_dict['channel']:
                        if message.content.isdigit():  # https://stackoverflow.com/questions/5606585/python-test-if-value-can-be-converted-to-an-int-in-a-list-comprehension
                            count_dict = self.coll.find_one(
                                {'_id': message.guild.id})  # return value for column for counting database
                            if count_dict is not None:
                                user_count_dict = self.coll_users.find_one(
                                    {'_id': message.guild.id}
                                )  # check if user has counted before. If they have, reply with the following message:
                                if user_count_dict is not None:
                                    if int(user_count_dict['user']) == int(message.author.id):
                                        return await message.reply("You can't count twice!")
                                    else:
                                        self.coll_users.update_one(
                                            {'_id': message.guild.id}, {"$set": {"user": message.author.id}}
                                        )
                                else:
                                    self.coll_users.insert_one({'_id': message.guild.id, 'user': message.author.id})

                                if int(message.content) == count_dict['count'] + 1:  # check if count is correct
                                    if (count_dict[
                                            'count'] + 1) % 100 == 0:  # add epic emojis for each counting milestone
                                        await message.add_reaction("<:100count:1107161672210206720>")
                                    elif (count_dict['count'] + 1) % 1000 == 0:
                                        await message.add_reaction("💫")
                                    elif (count_dict['count'] + 1) % 10000 == 0:
                                        await message.add_reaction("😀")
                                    await message.add_reaction("✅")
                                    self.coll.update_one({'_id': message.guild.id},
                                                         {'$inc': {'count': 1}})  # update count

                                else:
                                    await message.add_reaction("❌")
                            else:
                                self.coll.insert_one({'_id': message.guild.id, 'count': 1})

            except (TypeError, pymongo.errors.InvalidDocument, AttributeError) as e:
                pass

    @commands.slash_command(description="Get the current count for the server")
    async def count(self, ctx):
        count_dict = self.coll.find_one({'_id': ctx.guild.id})  # return value for column for counting database
        if count_dict is not None:
            embed = discord.Embed(
                title=f'Current Count for {ctx.guild.name}',
                description=f'{count_dict["count"]}',
                color=discord.Color.random()
            )
            await ctx.respond(embed=embed)

    async def catch(self,
                    val):  # the catch function makes sure that a server isn't None (for list comprehensions) see here: https://stackoverflow.com/questions/1528237/how-to-handle-exceptions-in-a-list-comprehensions
        try:
            if val is not None:
                return val.name
            else:
                return "Unknown server"
        except:
            return "Bot isn't in this server"

    @commands.slash_command(description='Get a leaderboard count for all servers that use counting')
    async def count_leaderboard(self, ctx):
        data = self.coll.find({})  # All servers listed in the count column
        servers = [server for server in data]
        embed = discord.Embed(
            title='Count Leaderboard',
            # https://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-a-value-of-the-dictionary
            description="".join(
                [str(await self.catch(self.bot.get_guild(i["_id"]))) + ": " + str(i["count"]) + "\n" for i in
                 sorted(servers, key=lambda d: d["count"], reverse=True)[:min(len(servers), 10)]]),
            # sort by count then get top 10 servers then format into proper string (also uses catch function to check if object doesn't return error)

            color=discord.Color.random()
        )
        await ctx.respond(embed=embed)


class SnakeGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class SnakeView(discord.ui.View):
        def __init__(self, c):
            super().__init__(disable_on_timeout=True, timeout=300)
            self.snake_class = c

        @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="🔼")
        async def callback_up(self, button, interaction):
            await interaction.response.defer()
            embed = self.message.embeds[0]

            if self.snake_class.move_up():
                self.disable_all_items()
                embed.title = 'You died!'
                embed.description = embed.description + f'\n Final Score: {self.snake_class.apples * 10}'
                await interaction.message.edit(view=self, embed=embed)
                return
            self.snake_class.tail_handle()

            embed.description = self.snake_class.return_grid()
            embed.description = embed.description + f'\n Score: {self.snake_class.apples * 10}'
            await interaction.message.edit(embed=self.message.embeds[0])

        @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="🔽")
        async def callback_down(self, button, interaction):
            await interaction.response.defer()
            embed = self.message.embeds[0]

            if self.snake_class.move_down():
                self.disable_all_items()
                embed.title = 'You died!'
                embed.description = embed.description + f'\n Final Score: {self.snake_class.apples * 10}'
                await interaction.message.edit(view=self, embed=embed)
                return
            self.snake_class.tail_handle()

            embed.description = self.snake_class.return_grid()
            embed.description = embed.description + f'\n Score: {self.snake_class.apples * 10}'
            await interaction.message.edit(embed=self.message.embeds[0])

        @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="◀")
        async def callback_left(self, button, interaction):
            await interaction.response.defer()
            embed = self.message.embeds[0]

            if self.snake_class.move_left():
                self.disable_all_items()
                embed.title = 'You died!'
                embed.description = embed.description + f'\n Final Score: {self.snake_class.apples * 10}'
                await interaction.message.edit(view=self, embed=embed)
                return
            self.snake_class.tail_handle()

            embed.description = self.snake_class.return_grid()
            embed.description = embed.description + f'\n Score: {self.snake_class.apples * 10}'
            await interaction.message.edit(embed=self.message.embeds[0])

        @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="▶")
        async def callback_right(self, button, interaction):
            await interaction.response.defer()
            embed = self.message.embeds[0]

            if self.snake_class.move_right():
                self.disable_all_items()
                embed.title = 'You died!'
                embed.description = embed.description + f'\n Final Score: {self.snake_class.apples * 10}'
                await interaction.message.edit(view=self, embed=embed)
                return
            self.snake_class.tail_handle()

            embed.description = self.snake_class.return_grid()
            embed.description = embed.description + f'\n Score: {self.snake_class.apples * 10}'
            await interaction.message.edit(embed=self.message.embeds[0])

    @commands.slash_command(description="Snake in discord!")
    async def snake(self, ctx):
        snake_class = snake.Snake(5)
        snake_class.start()
        embed = discord.Embed(
            title='Snake',
            description=snake_class.return_grid(),
            color=discord.Color.random()
        )
        snake_class.spawn_apple()
        await ctx.respond(embed=embed, view=self.SnakeView(snake_class))
