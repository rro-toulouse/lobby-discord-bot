import discord
from discord.ui import Button
from commands.match_lobby_commands import submit_score_command
from view.dropdown.result_dropdown import ResultDropdown

class SubmitScoreButton(Button):
    """
    Custom button that disables itself for a given timeout.
    :param label: The label to display on the button.
    :param style: The style of the button (danger, primary, etc.).
    :param timeout: Time in seconds before re-enabling the button (default 15 minutes).
    """
    def __init__(self, label: str, style: discord.ButtonStyle, match_id: int):
        super().__init__(label=label, style=style)
        self.match_id = match_id
        #self.disabled = True

    async def callback(self, interaction: discord.Interaction):
        dropdown = ResultDropdown(self.match_id)
        await interaction.response.send_message("Select the match result:", view=dropdown, ephemeral=True)
