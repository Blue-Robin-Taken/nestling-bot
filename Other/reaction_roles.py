from discord.ui import Button, View
import discord
from discord.ext import commands
from discord.ui.select import Select
import json
import pymongo
import enum


class ReactionRoles(commands.Cog):
    def __init__(self, bot, ):
        self.bot = bot

    class ReactionView(discord.ui.View):
        def __init__(self, roles):
            super().__init__(timeout=None)
            options = []
            for i in roles:
                print(i)
                options.append(discord.SelectOption(label=i.name))
            self.add_item(self.ReactionGetSelect(options))

        class ReactionGetSelect(
            discord.ui.Select):  # ReactionGetSelect is the select menu sent after the user selects the roles they want to use
            def __init__(self, options):
                if not options:
                    options = [" "]
                options.append(discord.SelectOption(label="Remove All Roles"))
                print(options)
                super().__init__(options=options, custom_id="MenuSelect", min_values=1, placeholder="Select a role",
                                 max_values=len(options))

            async def callback(self, interaction: discord.Interaction):
                if self.values[0] == "Remove All Roles":
                    print(self.options)
                    role = None
                    for i in self.options:

                        try:
                            try:
                                role = discord.utils.get(interaction.guild.roles, name=i.label)
                            except AttributeError:
                                pass
                            if role:
                                await interaction.response.send_message(f"Removed roles.", ephemeral=True)
                                return await interaction.user.remove_roles(role)
                        except discord.errors.Forbidden:
                            return await interaction.response.send_message("I don't have the proper permissions.", ephemeral=True)

                for i in self.values:
                    try:
                        role = discord.utils.get(interaction.guild.roles, name=i)
                        if role is not None:
                            await interaction.user.add_roles(discord.utils.get(interaction.guild.roles, name=i))
                    except discord.errors.Forbidden:
                        await interaction.response.send_message("I don't have the proper permissions.", ephemeral=True)
                await interaction.response.send_message(f"Added role {self.values[0]}.", ephemeral=True)

    class ReactionSelect(discord.ui.View):
        def __init__(self, channel, title, description, color):
            super().__init__(timeout=30)
            self.channel = channel
            self.title = title
            self.description = description
            self.color = color
            self.add_item(self.SelectOption(self))

        class SelectOption(discord.ui.Select):
            def __init__(self, parent):
                super().__init__(placeholder="Select a role", min_values=1,
                                 select_type=discord.ComponentType.role_select)
                self.parent = parent

            async def callback(self, interaction: discord.Interaction):
                if interaction.user.guild_permissions.administrator:
                    await interaction.response.send_message(f"{self.values}")
                    embed = discord.Embed(title=self.parent.title, description=self.parent.description,
                                          color=self.parent.color)
                    message = await self.parent.channel.send(embed=embed)
                    view = ReactionRoles.ReactionView(self.values)
                    await message.edit(view=view)
                else:
                    await interaction.response.send_message("You don't have permission to do that! (Need administrator)", ephemeral=True)

    @commands.slash_command(name="reactionroles",
                            description="(COMMAND IN PROGRESS) Create a reaction role message (With buttons!)")
    async def reactionroles(self, ctx, channel: discord.Option(discord.TextChannel), title: str,
                            description: discord.Option(str, required=False),
                            color_r: discord.Option(int, required=False) = 0, color_g: discord.Option(int, required=False) = 0, color_b: discord.Option(int, required=False) = 0):
        if ctx.author.guild_permissions.administrator:
            color = discord.Color.from_rgb(r=color_r, g=color_g, b=color_b)
            await ctx.defer()
            message = await ctx.respond(
                embed=discord.Embed(title=f"Choose what roles you want!",
                                    description="This will be in the reaction role message",
                                    color=color))
            view = self.ReactionSelect(channel, title, description, color)
            await message.edit(view=view)
        else:
            await ctx.respond("You don't have permission to do that! (Need administrator)", ephemeral=True)