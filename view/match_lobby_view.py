from datetime import datetime, timedelta
import discord
from discord import Embed
from discord.ui import View
import pytz
from database.constants import FINISH_MATCH_AFTER_IN_SEC
from database.enums import MatchStep
from services.match_service import get_match_by_id
from utils.user_utils import get_member_name_by_id
from view.buttons.join_match_button import JoinMatchButton
from view.buttons.leave_match_button import LeaveMatchButton
from view.buttons.ready_toggle_button import ReadyToggleButton
from view.buttons.start_match_button import StartMatchButton
from view.buttons.switch_team_button import SwitchTeamButton
from view.dropdown.player_management_dropdown import PlayerActionDropdown
from view.dropdown.result_dropdown import ResultDropdown

# Lobby Functionality
class MatchLobbyView(View):
    def __init__(self, match_id: int, player_list: dict):
        super().__init__(timeout=None)

        match = get_match_by_id(match_id)
        if (match.state == MatchStep.IN_CONSTRUCTION):
            self.add_item(JoinMatchButton(label="Join", style=discord.ButtonStyle.green, match_id=match_id))
            self.add_item(ReadyToggleButton(label="✅ Ready", style=discord.ButtonStyle.gray))
            self.add_item(SwitchTeamButton(label="Switch Team", style=discord.ButtonStyle.gray, match_id=match_id))
            self.add_item(LeaveMatchButton(label="Leave", style=discord.ButtonStyle.danger, match_id=match_id))
            self.add_item(StartMatchButton(label="Start", style=discord.ButtonStyle.primary, match_id=match_id, creator_id=match.creator_id))
            self.add_item(PlayerActionDropdown(label="Select a player to manage...", match_id=match_id, player_list=player_list, creator_id=match.creator_id))
         
        elif (match.state == MatchStep.IN_PROGRESS):
            # Business rule : Can enter score after a delay
            if (match.start_datetime + timedelta(seconds=FINISH_MATCH_AFTER_IN_SEC) <= datetime.now(pytz.timezone('CET'))): 
                self.add_item(ResultDropdown(label="Select Match Result", style=discord.ButtonStyle.green, match_id=match_id))

class MatchLobbyEmbed(Embed):
    description = ""
    def __init__(self, game_type):
        super().__init__()

        self.description = f"Game Type: **{game_type}**\n"
        discord.Embed(
            title="New Match Created!",
            description=self.description ,
            color=discord.Color.blue()
        )

    async def _init(self, channel: discord.TextChannel, creator_id: int):
        creator_name = await get_member_name_by_id(channel, creator_id)

        self.description  += f"Created by: **{creator_name}**\n\n" 
        self.description  += f"**Team A:**\n{creator_name} 👑 \n\n"
        self.description  += f"**Team B:**"