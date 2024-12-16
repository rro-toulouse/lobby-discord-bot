import discord
from discord.ui import Button
from commands.match_lobby_commands import ready_toggle_command

class ReadyToggleButton(Button):
    def __init__(self, label: str, style: discord.ButtonStyle):
        super().__init__(label=label, style=style)

    async def callback(self, interaction: discord.Interaction):
        await ready_toggle_command(interaction)