import discord
from discord.ui import Select

from database.constants import DELETE_MESSAGE_AFTER_IN_SEC
from view.player_action_view import PlayerActionConfirm

class PlayerActionDropdown(Select):
    def __init__(self, label: str, match_id: int, player_list: dict, creator_id: int):
        self.match_id = match_id
        self.creator_id = creator_id

        # Options for each player
        options = [
            discord.SelectOption(label=f"{player['name']}", description=f"ID: {player['id']}", value=str(player['id']))
            for player in player_list
        ]

        # Add generic actions for dropdown
        options.append(discord.SelectOption(label="Cancel", description="Exit without action", value="cancel"))

        super().__init__(placeholder=label, options=options)

    async def callback(self, interaction: discord.Interaction):
        player_id = int(self.values[0]) if self.values[0] != "cancel" else None

        if self.values[0] == "cancel" or player_id == None or not player_id:
            await interaction.response.send_message("❌ Action canceled.", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
            return
        
        user_id = interaction.user.id
        if user_id != self.creator_id:
            await interaction.response.send_message("❌ Only the match leader can manage players!", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
            return

        # Present kick/ban options
        view = PlayerActionConfirm(self.match_id, player_id)
        await interaction.response.send_message(
            content=f"What action would you like to take for player **<@{player_id}>**?", view=view, ephemeral=True, 
        )