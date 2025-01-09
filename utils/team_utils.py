import discord

from models.Match import Match
from services.match_service import check_ready_by_player_id
from utils.user_utils import get_member_name_by_id

async def set_teams_composition(channel: discord.TextChannel, team_name: str, team_list, match: Match):
    teams_composition = team_name + "\n"
    for player_id in team_list: 
        if check_ready_by_player_id(player_id, match.id):
            teams_composition += "✅ "
        teams_composition += await get_member_name_by_id(channel, player_id)
        if (player_id == match.creator_id):
            teams_composition += " 👑"
        if (player_id != team_list[-1]):
            teams_composition += "\n"
    return teams_composition

async def player_ids_to_dict(channel: discord.TextChannel, player_ids: list[int]):
    player_list = [{"id": int(player_id), "name": await get_member_name_by_id(channel, int(player_id))} for player_id in player_ids]
    return player_list

   