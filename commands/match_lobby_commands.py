import discord
import pytz
from datetime import datetime, timedelta
from database.enums import MatchStep
from services.match_service import clear_players_ready, get_match_by_id, get_match_by_user_id, player_ready_toggle, update_match, delete_match
from services.lobby_service import refresh_match_in_lobby
from database.constants import DELETE_MESSAGE_AFTER_IN_SEC, FINISH_MATCH_AFTER_IN_SEC

"""Handle joining a match."""
async def join_match_command(interaction: discord.Interaction, match_id: int):
        user_id = interaction.user.id
        match = get_match_by_id(match_id)

        if not match:
            await interaction.response.send_message("❌ Match does not exist!", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
            return

        team_a = match.team_a
        team_b = match.team_b

        if user_id in team_a or user_id in team_b:
            await interaction.response.send_message("❌ You are already in this match!", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
            return

        # Add to Team A if it's smaller; else add to Team B
        if len(team_a) <= len(team_b):
            team_a.append(user_id)
        else:
            team_b.append(user_id)

        clear_players_ready(match.id) # Reset ready status
        update_match(match_id, team_a_players=team_a, team_b_players=team_b)
        await refresh_match_in_lobby(interaction.channel, match, team_a, team_b, user_id)
        await interaction.response.send_message(f"✅ {interaction.user.mention} joined the match!", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)

 
async def ready_toggle_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    match = get_match_by_user_id(user_id)
    if not match:
        await interaction.response.send_message("❌ You are not part of any match.", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        return
    
    if player_ready_toggle(user_id, match.id):
        await interaction.response.send_message("✅ You are now ready!", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)           
    else:
        await interaction.response.send_message("❌ You are no longer ready.", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
                
    await refresh_match_in_lobby(interaction.channel, match, match.team_a, match.team_b, user_id)

"""Switch the player's team."""
async def switch_team_command(interaction: discord.Interaction, match_id: int):
    user_id = interaction.user.id
    match = get_match_by_id(match_id)

    if not match:
        await interaction.response.send_message("❌ Match does not exist!", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        return
    
    team_a = match.team_a
    team_b = match.team_b

    clear_players_ready(match.id) # Reset ready status
    if user_id in team_a:
        team_a.remove(user_id)
        team_b.append(user_id)
        await refresh_match_in_lobby(interaction.channel, match, team_a, team_b, user_id)
        message = f"✅ {interaction.user.mention} switched to Team B!"
    elif user_id in team_b:
        team_b.remove(user_id)
        team_a.append(user_id)
        await refresh_match_in_lobby(interaction.channel, match, team_a, team_b, user_id)
        message = f"✅ {interaction.user.mention} switched to Team A!"
    else:
        await interaction.response.send_message("❌ You are not part of any team!", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        return

    update_match(match_id, team_a_players=team_a, team_b_players=team_b)
    await interaction.response.send_message(message, ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)

"""Allow a user to leave the match."""
async def leave_match_command(interaction: discord.Interaction, match_id: int):
    user_id = interaction.user.id
    match = get_match_by_id(match_id)

    if not match:
        await interaction.response.send_message("❌ Match does not exist!", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        return

    team_a = match.team_a
    team_b = match.team_b

    if user_id in team_a:
        team_a.remove(user_id)
    elif user_id in team_b:
        team_b.remove(user_id)
    else:
        await interaction.response.send_message("❌ You are not part of this match!", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        return

    if len(team_a) == 0 and len(team_b) == 0:
        delete_match(match_id)
        await interaction.response.send_message("✅ You left the match. The match has been deleted as no players remain.", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        await refresh_match_in_lobby(interaction.channel, match, team_a, team_b, user_id)
        return
    else:
        clear_players_ready(match.id) # Reset ready status
        if user_id == match.creator_id:
            new_creator = team_a[0] if len(team_a) else team_b[0]
            update_match(match_id, team_a_players=team_a, team_b_players=team_b, creator_id=new_creator)
            await interaction.response.send_message(f"✅ You left the match. Leadership has been transferred to <@{new_creator}>.", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        else:
            update_match(match_id, team_a_players=team_a, team_b_players=team_b)
            await interaction.response.send_message("✅ You left the match.", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        match = get_match_by_id(match_id)
        await refresh_match_in_lobby(interaction.channel, match, team_a, team_b, user_id)

"""Handle starting a match."""
async def start_match_command(interaction: discord.Interaction, match_id: int, creator_id: int):
    user_id = interaction.user.id
    if user_id != creator_id:
        await interaction.response.send_message("❌ Only the war leader can start the match!", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        return

    match = get_match_by_id(match_id)
    if not match:
        await interaction.response.send_message("❌ Match does not exist!", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        return

    # Business rules
    team_a = match.team_a
    team_b = match.team_b
    all_players = set(match.team_a + match.team_b)
    if (len(team_a) != len(team_b)):
        await interaction.response.send_message("❌ Not same number of players in both teams !", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        return
    elif (len(team_a) < 1):
    #elif (len(team_a) < 2):
        await interaction.response.send_message("❌ Need at least 2 players in both teams !", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        return
    # TODO Display Close Match button only when match is started
    elif (sorted(match.ready_players) != sorted(all_players)):
        await interaction.response.send_message("❌ Not all players are ready. Please wait until everyone sets their status to ready.", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        return
    else:
        update_match(match_id, state=MatchStep.IN_PROGRESS)
        await interaction.response.send_message("✅ Match started! No more players can join.", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        finish_match_time = datetime.now(pytz.timezone('CET')) + timedelta(seconds=FINISH_MATCH_AFTER_IN_SEC)
        #await interaction.message.edit(content=f"--\n⏳ Match in progress!\nCan be finished at CET {finish_match_time.strftime('%H:%M:%S')}", view=None)
        await interaction.message.edit(content=f"--\n⏳ Match in progress!", view=None)
        await refresh_match_in_lobby(interaction.channel, match, team_a, team_b, user_id)

async def submit_score_command(interaction: discord.Interaction, match_id: int):
    user_id = interaction.user.id
    match = get_match_by_id(match_id)
    
    if not match:
        await interaction.response.send_message("❌ Match does not exist!", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        return

    # TODO Add score input interface

    if match.state != MatchStep.IN_PROGRESS:  
        await interaction.response.send_message("❌ Match has to be started first!", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        return
    else:
        update_match(match_id, state=MatchStep.DONE)
        match = get_match_by_id(match_id)
        await refresh_match_in_lobby(interaction.channel, match, match.team_a, match.team_b, user_id)

    # TODO Add match to history channel