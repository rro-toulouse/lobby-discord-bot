import discord
from database.Match import Match
from database.constants import WAR_CHANNEL_NAME_END,  WAR_CHANNEL_NAME_START
from database.enums import MatchStep
from utils.team_utils import set_teams_composition

# Dictionary with key=match_id and value=message_data 
posted_war_message_dict = {}

async def add_match_to_lobby(channel: discord.TextChannel, match_id, game_type, creator_id):
    """
    Posts / update match details in the lobby channel with a "Join Match" button.
    """
    from view.match_lobby_view import MatchLobbyView, MatchLobbyEmbed

    view = MatchLobbyView(match_id=match_id, user_id=creator_id)
    embed = MatchLobbyEmbed(game_type)
    await embed._init(channel, creator_id)

    if not match_id in posted_war_message_dict:
        posted_war_message_dict[match_id] = await channel.send(embed=embed, view=view)
    else:
        print("Warning: A match with this ID already exists.")
        return

async def refresh_match_in_lobby(channel: discord.TextChannel, match: Match, team_a, team_b, user_id):
    if match is None or not match.id in posted_war_message_dict: # Match does not exist
        print("Warning: Match does not exist in local list")
        return
    elif (len(team_a) == 0 and len(team_b) == 0) or match.state == MatchStep.DONE: # Match is now empty or finished, delete it
        msg = await channel.fetch_message(posted_war_message_dict[match.id].id)
        await msg.delete()
        posted_war_message_dict.pop(match.id, None)
    else: # Refresh view and embed
        message = posted_war_message_dict[match.id]
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

        view = MatchLobbyView(match.id, user_id)
        await message.edit(view=view)
    
    # Refresh channel name
    await channel.edit(name=WAR_CHANNEL_NAME_START + str(len(posted_war_message_dict)) + WAR_CHANNEL_NAME_END)
   