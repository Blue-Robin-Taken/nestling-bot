from discord.ui import Button, View
import discord
from discord.ext import commands
from discord.ui.select import Select
import json
import pymongo

client = pymongo.MongoClient(
    "mongodb+srv://BlueRobin:ZaJleEpNhBUxqMDK@nestling-bot-settings.8n1wpmw.mongodb.net/?retryWrites=true&w=majority")
db = client.settings


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class basicButton(Button):
        def __init__(self, row, label, user, selection, index):
            super().__init__(style=discord.ButtonStyle.blurple, label=label, row=row)
            self.values = []
            self.user = user
            self.selection = selection
            self.index = index

        async def callback(self, interaction):
            if interaction.user.id == self.user.id:
                self.view.disable_all_items()
                await interaction.message.edit(view=self.view)
                label = self.label
                selection = self.selection

                class baseSelect(Select):
                    def __init__(self, options, **kwargs):
                        super().__init__(options=options, **kwargs)

                    async def callback(self, i):
                        if i.user.id == interaction.user.id:
                            self.view.disable_all_items()
                            await i.message.edit(view=self.view)
                            if selection == "text_channel":
                                coll = getattr(db, f"{label}")
                                # channel
                                c = discord.utils.get(interaction.guild.text_channels, name=self.values[0]).id
                                # noinspection PyUnresolvedReferences
                                # The above line is for the editor Pycharm
                                try:
                                    coll.insert_one({"_id": interaction.guild.id, "channel": c})
                                except pymongo.errors.DuplicateKeyError:
                                    coll.update_one({"_id": interaction.guild.id}, {"$set": {"channel": c}})
                                await i.response.send_message('Set Channel')
                            elif selection == "roles":
                                coll = getattr(db, f"{label}")
                                # channel
                                c = discord.utils.get(interaction.guild.roles, name=self.values[0]).id
                                # noinspection PyUnresolvedReferences
                                # The above line is for the editor Pycharm
                                try:
                                    coll.insert_one({"_id": interaction.guild.id, "role": c})
                                except pymongo.errors.DuplicateKeyError:
                                    coll.update_one({"_id": interaction.guild.id}, {"$set": {"role": c}})
                                await i.response.send_message('Set Role')
                        else:
                            await i.response.send_message("You don't have permission to do that!", ephemeral=True)

                embed = discord.Embed(
                    title=f"{self.label}",
                    description="Select a setting: ",
                    color=discord.Color.random()
                )
                message = await interaction.response.send_message(embed=embed)
                view = View()
                options_list = list()
                selects = list()
                guild = interaction.guild
                if self.selection == 'text_channel':
                    for channel in guild.text_channels:
                        if len(options_list) >= 20:
                            selects.append(Select(options=options_list))
                            options_list = []
                        else:
                            options_list.append(discord.SelectOption(label=channel.name))
                    selects.append(baseSelect(options=options_list))
                    for select in selects:
                        view.add_item(select)
                elif self.selection == 'roles':
                    for role in guild.roles:
                        if role.name != "@everyone":
                            if len(options_list) >= 20:
                                selects.append(Select(options=options_list))
                                options_list = []
                            else:
                                options_list.append(discord.SelectOption(label=role.name))
                    selects.append(baseSelect(options=options_list))
                    for select in selects:
                        view.add_item(select)
                await message.edit_original_response(embed=embed, view=view)
            else:
                await interaction.response.send_message("You don't have permission to do that!", ephemeral=True)

    @commands.slash_command(name="settings", description="Change some settings.")
    async def settings(self, ctx):
        if ctx.user.guild_permissions.administrator:
            settings = [{'Suggestion Channel': 'text_channel'},
                        {'Auto Role': 'roles'}]
            embedString = "".join([f'\n **{i + 1}**: {list(settings[i].keys())[0]}' for i in range(len(settings))])
            embed = discord.Embed(
                title="Settings",
                description=f"Select a setting: {embedString}",
                color=discord.Color.random()
            )
            message = await ctx.respond(embed=embed)
            view = View()
            for i in range(len(settings)):
                view.add_item(
                    self.basicButton(0, list(settings[i].keys())[0], ctx.user, selection=list(settings[i].values())[0],
                                     index=i))
            await message.edit_original_response(view=view)
        else:
            await ctx.respond("You need administrator privileges to access this.", ephemeral=True)
