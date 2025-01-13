import discord
from discord.ui import Select

from commands.match_lobby_commands import submit_score_command
from database.enums import MatchIssue

class ResultDropdown(Select):
    def __init__(self, label: str, style: discord.ButtonStyle, match_id: int):
        self.match_id = match_id

        options=[
            discord.SelectOption(label="Team A Won", value=MatchIssue.TEAM_A_WON.value),
            discord.SelectOption(label="Team B Won", value=MatchIssue.TEAM_B_WON.value),
            discord.SelectOption(label="Draw", value=MatchIssue.DRAW.value),
            discord.SelectOption(label="Match Canceled", value=MatchIssue.CANCEL.value),
        ]
        super().__init__(placeholder=label, min_values=1, max_values=1, options=options)
        
    async def interaction_check(self, interaction: discord.Interaction):
        await submit_score_command(interaction, self.values[0], self.match_id)
