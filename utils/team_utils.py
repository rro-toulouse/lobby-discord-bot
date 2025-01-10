import discord

from database.enums import MatchIssue, MatchStep
from models.Match import Match
from services.match_service import check_ready_by_player_id, get_match_vote_for_a_player
from utils.user_utils import get_member_name_by_id

def retrieve_vote_text(vote: MatchIssue) -> str:
    if vote == MatchIssue.TEAM_A_WON:
        return "🅰️"
    elif vote == MatchIssue.TEAM_B_WON:
        return "🅱️"
    elif vote ==  MatchIssue.DRAW:
        return "🆎"
    elif vote ==  MatchIssue.CANCEL:
        return "❌"

async def set_teams_composition(channel: discord.TextChannel, team_name: str, team_list, match: Match):
    players_vote = dict()

    # Players match result vote
    if (match.state == MatchStep.IN_PROGRESS):
        for player_id in team_list:
            match_issue = get_match_vote_for_a_player(match.id, player_id)
            if match_issue is not None:
                players_vote[player_id] = match_issue

    teams_composition = team_name + "\n"
    for player_id in team_list: 
        if check_ready_by_player_id(player_id, match.id):
            teams_composition += "✅ "
        teams_composition += await get_member_name_by_id(channel, player_id)
        if (player_id == match.creator_id):
            teams_composition += " 👑"

        # Players match result vote
        if match.state == MatchStep.IN_PROGRESS and len(players_vote) > 0:
            if player_id in players_vote:

                teams_composition += " - " + retrieve_vote_text(players_vote[player_id])

        if (player_id != team_list[-1]):
            teams_composition += "\n"
    return teams_composition

async def player_ids_to_dict(channel: discord.TextChannel, player_ids: list[int]):
    player_list = [{"id": int(player_id), "name": await get_member_name_by_id(channel, int(player_id))} for player_id in player_ids]
    return player_list

   