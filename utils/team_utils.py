import discord

async def get_team_names(team_ids):
    team_names = []
    for player_id in team_ids:
        try:
            # TODO Retrieve names but from channel
            # Retrieve the member from the API
            #users = bot.get_guild(DISCORD_SERVER_ID).fetch_members()
            #member = bot.get_user(player_id)
            #member = bot.fetch_user(player_id)
            member = str(player_id)
            if member is not None:
                team_names.append(member)
            else:
                print(f"Player id {player_id} (Not Found)")
        except discord.NotFound:
            # Member is not found, handle accordingly (e.g., player left server)
            team_names.append(f"Player {player_id} (Not Found)")
    return team_names

def set_teams_composition(team_name, team_list, creator_id):
    teams_composition = team_name
    for player in team_list:
        if (player == creator_id):
            teams_composition += "👑 "
        teams_composition += str(player) # TODO Convert to player name here
        if (player != team_list[-1]):
            teams_composition += ", "
    return teams_composition