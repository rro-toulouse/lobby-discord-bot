import discord
from database.Match import Match
from utils.team_utils import get_team_names, set_teams_composition

# Dictionary with key=match_id and value=message_data 
posted_war_message_dict = {}

async def add_match_to_lobby(channel: discord.TextChannel, match_id, game_type, creator_name, team_a, team_b):
    """
    Posts / update match details in the lobby channel with a "Join Match" button.
    """
    from view.match_lobby_view import MatchLobbyView, MatchLobbyEmbed

    view = MatchLobbyView(match_id, team_a[0])
    embed = MatchLobbyEmbed(game_type, creator_name)
    await embed._init(team_a, team_b)

    if not match_id in posted_war_message_dict:
        posted_war_message_dict[match_id] = await channel.send(embed=embed, view=view)
    else:
        print("Warning: A match with this ID already exists.")
        return

async def refresh_match_in_lobby(channel: discord.TextChannel, match: Match, team_a, team_b):
    if not match.id in posted_war_message_dict:
        print("Warining: Match does not exist in local list")
        return
    elif len(team_a) == 0 and len(team_b) == 0:
        msg = await channel.fetch_message(posted_war_message_dict[match.id].id)
        await msg.delete()
        posted_war_message_dict.pop(match.id, None)
    else:
        embed = posted_war_message_dict[match.id].embeds[0] 
        description_array = embed.description.splitlines()
             
        teams_composition_a = set_teams_composition("**Team A:** ", team_a, match.creator_id)
        teams_composition_b = set_teams_composition("**Team B:** ", team_b, match.creator_id)
     
        description_array[-2] = teams_composition_a
        description_array[-1] = teams_composition_b

        embed.description = "\n".join(description_array)
        await posted_war_message_dict[match.id].edit(embed=embed)
        return