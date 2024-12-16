import discord
from discord.ui import Button
from commands.match_lobby_commands import leave_match_command

class LeaveMatchButton(Button):
    def __init__(self, label: str, style: discord.ButtonStyle, match_id: int):
        super().__init__(label=label, style=style)
        self.match_id = match_id

    async def callback(self, interaction: discord.Interaction):
        await leave_match_command(interaction, self.match_id)