from discord.ui import Button, View
import discord
from discord.ext import commands
from discord.ui.select import Select
import json


class suggestButton(Button):
    def __init__(self, row, label, default, key, user, message):
        super().__init__(style=discord.ButtonStyle.blurple, label=label, row=row)
        self.default = default
        self.key = key
        self.user = user
        self.message = message

    async def callback(self, interaction):
        await interaction.response.defer()
        if interaction.user == self.user:
            message = await interaction.channel.send(self.key)
            categories = interaction.guild.categories
            options_list = []
            selects = []
            index = 0

            for category in categories:
                for channel in category.channels:
                    index += 1
                    if index > 20:
                        index = 0
                        selects.append(Select(options=options_list))
                        options_list = []
                    else:
                        if str(channel.type) == "text":
                            options_list.append(discord.SelectOption(label=channel.name, emoji="📜"))
            selects.append(Select(options=options_list))
            view = View()

            async def callback_select(i):
                await i.response.defer()
                if i.user == self.user:
                    selection = None
                    for select in selects:
                        if not select.values[0] is None:
                            selection = select.values[0]
                            break
                    self.view.disable_all_items()
                    embed = discord.Embed(
                        title=f"Setting changed by {self.user.name}",
                        description=f"The new suggestion channel is #{selection}",
                        color=discord.Color.random()
                    )
                    await i.message.edit(content=None, view=None, embed=embed)
                    await self.message.edit_original_response(view=None)

                    with open("settings.json", 'r') as file:
                        settings = json.load(file)
                    with open("settings.json", 'w') as file:
                        if str(interaction.guild.id) in settings.keys():
                            settings[str(interaction.guild.id)]["Suggestion Channel"] = str(
                                discord.utils.get(interaction.guild.channels, name=selection).id)
                        else:
                            settings[str(interaction.guild.id)] = self.default
                            settings[str(interaction.guild.id)]["Suggestion Channel"] = str(
                                discord.utils.get(interaction.guild.channels, name=selection).id)
                        json.dump(settings, file)
                else:
                    await i.response.send_message("You don't have permission to do that!", ephemeral=True)

            for select in selects:
                select.callback = callback_select
                view.add_item(select)
            await message.edit(view=view)
        else:
            await interaction.response.send_message("You don't have permission to do that!", ephemeral=True)

# class suggestButton(Button):
#     def __init__(self, row, label, default, key, user, message):
#         super().__init__(style=discord.ButtonStyle.blurple, label=label, row=row)
#         self.default = default
#         self.key = key
#         self.user = user
#         self.message = message
#
#     async def callback(self, interaction):

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="settings", description="Change some settings.")
    async def settings(self, ctx):
        if ctx.user.guild_permissions.administrator:
            defaultSettingsList = {"Suggestion Channel": None}
            embed = discord.Embed(
                title="Settings",
                description="Select a setting: ",
                color=discord.Color.random()
            )
            index = 0
            for i in defaultSettingsList.keys():  # Create embed of all the settings
                index += 1
                embed.add_field(name=f"{index}:", value=i, inline=False)
            message = await ctx.respond("Select a setting: ", embed=embed)
            view = View()  # Set view

            index = 0
            for i in defaultSettingsList.keys():  # Create buttons for all settings
                index += 1
                view.add_item(suggestButton(0, str(index), defaultSettingsList, i, ctx.user, message))
            await message.edit_original_response(view=view)  # Edit view into message
        else:
            await ctx.respond("You need administrator privileges to access this.", ephemeral=True)
