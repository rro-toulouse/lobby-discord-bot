import discord
from discord.ui import Button
from commands.match_lobby_commands import kick_player_command

class KickButton(Button):
    def __init__(self, match_id, player_id):
        super().__init__(label="Kick", style=discord.ButtonStyle.danger)
        self.match_id = match_id
        self.player_id = player_id

    async def callback(self, interaction: discord.Interaction):
        await kick_player_command(interaction, self.player_id, self.match_id)