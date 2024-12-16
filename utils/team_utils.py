import discord

from database.Match import Match
from services.match_service import check_ready_by_player_id

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

async def get_member_name_by_id(channel: discord.TextChannel, id: int):
    guild = channel.guild
    if (guild is None):
        print(f"Player id {id} (Not Found)")
        return str(id)
    member = await guild.fetch_member(id)
    if (member is None):
        print(f"Player id {id} (Not Found)")
        return str(id)
    return member.display_name
