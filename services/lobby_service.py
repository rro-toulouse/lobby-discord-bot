import discord
from models.Match import Match
from database.enums import MatchStep
from services.match_service import get_players
from utils.team_utils import player_ids_to_dict, set_teams_composition

# Dictionary with key=match_id and value=message_data 
posted_match_message_dict = {}

"""
Posts / update match details in the lobby channel with a "Join Match" button.
"""
async def add_match_to_lobby(channel: discord.TextChannel, match_id, game_type, creator_id):
    
    from view.match_lobby_view import MatchLobbyView, MatchLobbyEmbed

    players_ids = get_players(match_id)
    player_list = await player_ids_to_dict(channel, players_ids)
    view = MatchLobbyView(match_id=match_id, player_list=player_list)
    embed = MatchLobbyEmbed(game_type)
    await embed._init(channel, creator_id)

    if not match_id in posted_match_message_dict:
        posted_match_message_dict[match_id] = await channel.send(embed=embed, view=view)
    else:
        print("Warning: A match with this ID already exists.")
        return
    
async def delete_match_from_lobby(channel: discord.TextChannel, match: Match):
    try:
        msg = await channel.fetch_message(posted_match_message_dict[match.id].id)
        await msg.delete()
        posted_match_message_dict.pop(match.id, None)
    except discord.NotFound as error:
        print(f"Error during delete_match_from_lobby: Message ID {posted_match_message_dict[match.id].id} not found in channel ID {channel.id}")
    except Exception as error:
        print(f"Error occurred during delete_match_from_lobby: {error}")

async def refresh_match_in_lobby(channel: discord.TextChannel, match: Match, team_a, team_b):
    if match is None or not match.id in posted_match_message_dict: # Match does not exist
        print("Warning: Match does not exist in local list")
        return
    elif (len(team_a) == 0 and len(team_b) == 0) or match.state == MatchStep.DONE: # Match is now empty or finished, delete it
        await delete_match_from_lobby(channel, match)
    else: # Refresh view and embed
        message = posted_match_message_dict[match.id]
        embed = message.embeds[0] 

        # Embed update
        description_array = embed.description.splitlines()
        description_str = description_array[0] + "\n" + description_array[1] + "\n\n"
             
        teams_composition_a = await set_teams_composition(channel, "**Team A:**", team_a, match)
        teams_composition_b = await set_teams_composition(channel, "**Team B:**", team_b, match)
     
        description_str += teams_composition_a + "\n\n"
        description_str += teams_composition_b

        embed.description = description_str

        await message.edit(embed=embed)
        
        # View update
        from view.match_lobby_view import MatchLobbyView

        players_ids = get_players(match.id)
        player_list = await player_ids_to_dict(channel, players_ids)
        view = MatchLobbyView(match_id=match.id, player_list=player_list)
        await message.edit(view=view)
    
    # Refresh channel name
    #await channel.edit(name=MATCH_CHANNEL_NAME_START + str(len(posted_match_message_dict)) + MATCH_CHANNEL_NAME_END)
   