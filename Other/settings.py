from discord.ui import Button, View
import discord
from discord.ext import commands
from discord.ui.select import Select
import json
import pymongo
import os

client = pymongo.MongoClient(
     f"mongodb+srv://BlueRobin:{os.getenv('MongoPass')}@nestling-bot-settings.8n1wpmw.mongodb.net/?retryWrites=true&w=majority")
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
                    def __init__(self, **kwargs):
                        super().__init__(**kwargs)

                    async def callback(self, i):
                        print(self.type)
                        if i.user.id == interaction.user.id:
                            self.view.disable_all_items()
                            await i.message.edit(view=self.view)
                            if self.channel_types == [discord.ChannelType.text]:
                                coll = getattr(db, f"{label}")
                                # channel
                                c = self.values[0].id
                                # noinspection PyUnresolvedReferences
                                # The above line is for the editor Pycharm
                                try:
                                    coll.insert_one({"_id": interaction.guild.id, "channel": c})
                                except pymongo.errors.DuplicateKeyError:
                                    coll.update_one({"_id": interaction.guild.id}, {"$set": {"channel": c}})
                                await i.response.send_message('Set Channel')
                            elif self.type == discord.ComponentType.role_select:
                                coll = getattr(db, f"{label}")
                                # channel
                                c = self.values[0].id
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

                if self.selection == 'text_channel':
                    selection = baseSelect(select_type=discord.ComponentType.channel_select, channel_types=[discord.ChannelType.text])
                    view.add_item(selection)
                elif self.selection == 'roles':
                    selection = baseSelect(select_type=discord.ComponentType.role_select)
                    view.add_item(selection)
                try:
                    seen = set()
                    view.children = [x for x in view.children if x not in seen and not seen.add(x)]
                    await message.edit_original_response(embed=embed, view=view)
                except discord.HTTPException as e:
                    print(e)
                    await message.edit_original_response(embed=embed)
            else:
                await interaction.response.send_message("You don't have permission to do that!", ephemeral=True)

    @commands.slash_command(name="settings", description="Change some settings.")
    async def settings(self, ctx):
        if ctx.user.guild_permissions.administrator:
            settings = [{'Suggestion Channel': 'text_channel'},
                        {'Auto Role': 'roles'}, {'Counting Channel': 'text_channel'}, {''}]
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
