import os
import discord
import pytz
from datetime import datetime, timedelta
from database.enums import MatchStep
from services.match_service import add_match_vote, ban_player_from_match, clear_players_ready, finalize_match, get_match_by_id, get_match_by_user_id, is_user_already_in_match, is_user_banned, is_user_in_match_id, player_ready_toggle, post_match_to_history_channel, update_match, delete_match
from services.lobby_service import refresh_match_in_lobby
from database.constants import DELETE_MESSAGE_AFTER_IN_SEC, FINISH_MATCH_AFTER_IN_SEC
from services.player_service import ensure_player_in_db
from utils.match_utils import enter_match_result_callback, on_match_action, start_enter_match_result_timer
from utils.team_utils import compute_team_average_elo

"""Handle joining a match."""
async def join_match_command(interaction: discord.Interaction, match_id: int):
        ensure_player_in_db(interaction.user)
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

        if is_user_already_in_match(user_id):
            await interaction.response.send_message("❌ You are already in a match, please leave it before joining this one!", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
            return

        if is_user_banned(match_id, user_id):
            await interaction.response.send_message("❌ You are banned from this match!", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
            return

        # Add to Team A if it's smaller; else add to Team B
        if len(team_a) <= len(team_b):
            team_a.append(user_id)
        else:
            team_b.append(user_id)

        clear_players_ready(match.id) # Reset ready status
        update_match(match_id, team_a_players=team_a, team_b_players=team_b)
        await on_match_action(match_id, interaction.channel)
        await refresh_match_in_lobby(interaction.channel, match, team_a, team_b)
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

    await on_match_action(match.id, interaction.channel)            
    await refresh_match_in_lobby(interaction.channel, match, match.team_a, match.team_b)

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
        await refresh_match_in_lobby(interaction.channel, match, team_a, team_b)
        message = f"✅ {interaction.user.mention} switched to Team B!"
    elif user_id in team_b:
        team_b.remove(user_id)
        team_a.append(user_id)
        await refresh_match_in_lobby(interaction.channel, match, team_a, team_b)
        message = f"✅ {interaction.user.mention} switched to Team A!"
    else:
        await interaction.response.send_message("❌ You are not part of any team!", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        return

    await on_match_action(match_id, interaction.channel)
    update_match(match_id, team_a_players=team_a, team_b_players=team_b)
    await interaction.response.send_message(message, ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)

"""Allow a user to leave the match."""
async def leave_match_command(interaction: discord.Interaction, match_id: int, player_id: int = -1, kick: bool = False):
    if (player_id == -1):
        user_id = interaction.user.id
    else:
        user_id = player_id
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
        if kick is False:
            await interaction.response.send_message(f"✅ **<@{player_id}>** has left the match. The match has been deleted as no players remain.", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        await refresh_match_in_lobby(interaction.channel, match, team_a, team_b)
        return
    else:
        clear_players_ready(match.id) # Reset ready status
        if user_id == match.creator_id:
            new_creator = team_a[0] if len(team_a) else team_b[0]
            update_match(match_id, team_a_players=team_a, team_b_players=team_b, creator_id=new_creator)
            if kick is False:
                await interaction.response.send_message(f"✅ **<@{player_id}>** has left the match. Leadership has been transferred to <@{new_creator}>.", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        else:
            update_match(match_id, team_a_players=team_a, team_b_players=team_b)
            if kick is False:
                await interaction.response.send_message(f"✅ **<@{player_id}>** has left the match.", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        match = get_match_by_id(match_id)
        await refresh_match_in_lobby(interaction.channel, match, team_a, team_b)
    await on_match_action(match_id, interaction.channel)

"""Handle starting a match."""
async def start_match_command(interaction: discord.Interaction, match_id: int, creator_id: int):
    user_id = interaction.user.id
    if user_id != creator_id:
        await interaction.response.send_message("❌ Only the match leader can start the match!", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
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
    elif (len(team_a) < 1): # Dev purpose
    #elif (len(team_a) < 2):
        await interaction.response.send_message("❌ Need at least 2 players in both teams !", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        return
    elif (sorted(match.ready_players) != sorted(all_players)):
        await interaction.response.send_message("❌ Not all players are ready. Please wait until everyone sets their status to ready.", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        return
    else:
        finish_match_time = datetime.now(pytz.timezone('CET')) + timedelta(seconds=FINISH_MATCH_AFTER_IN_SEC)
        update_match(match_id, 
                     state=MatchStep.IN_PROGRESS, 
                     start_datetime=datetime.now(pytz.timezone('CET')))
        await start_enter_match_result_timer(match_id, interaction.channel, FINISH_MATCH_AFTER_IN_SEC, enter_match_result_callback)
        await interaction.response.send_message("✅ Match started! No more players can join.", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        await interaction.message.edit(content=f"⏳ Match in progress!\nCan be finished at CET {finish_match_time.strftime('%H:%M:%S')}", view=None)
        await refresh_match_in_lobby(interaction.channel, match, team_a, team_b)

async def submit_score_command(interaction: discord.Interaction, result:str, match_id: int):
    user_id = interaction.user.id
    match = get_match_by_id(match_id)
    
    if not match:
        await interaction.response.send_message("❌ Match does not exist!", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        return

    if not is_user_in_match_id(user_id, match.id):
        await interaction.response.send_message("❌ You are not part of this match.", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        return
    
    if match.state != MatchStep.IN_PROGRESS:  
        await interaction.response.send_message("❌ Match has to be started first!", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
        return

    votes = add_match_vote(user_id, match.id, result)

    # Business rule : Vote condition to close a player match 
    threshold = (len(match.team_a) + len(match.team_b) // 2) + 1
    finished = False

    for vote in votes:
        nb_vote = vote[1]
        if nb_vote >= threshold:
            finalize_match(match.id, result)    
            update_match(match_id, state=MatchStep.DONE,
                     team_a_elo=compute_team_average_elo(match.team_a, match.game_type), 
                     team_b_elo=compute_team_average_elo(match.team_b, match.game_type))
            match = get_match_by_id(match_id)
            await interaction.response.send_message("✅ Match finalized!", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
            
            MATCH_HISTORY_CHANNEL = os.getenv("MATCH_HISTORY_CHANNEL_ID")
            history_channel = interaction.guild.get_channel(int(MATCH_HISTORY_CHANNEL)) # Fetch the channel by ID
            if history_channel:
                    await post_match_to_history_channel(
                        channel=history_channel,
                        match=match)
            else:
                await interaction.response.send_message("❌ Can't add match to match history", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
            finished = True
            break

    if finished == False:
        await interaction.response.send_message(f"✅ Vote registered. Waiting for more similar votes...", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)

    match = get_match_by_id(match_id)
    await refresh_match_in_lobby(interaction.channel, match, match.team_a, match.team_b)

async def kick_player_command(interaction: discord.Interaction, player_id: int, match_id: int):
    await leave_match_command(interaction, match_id, player_id, True)
    
    match = get_match_by_id(match_id)
    if match is None:
        return
    await refresh_match_in_lobby(interaction.channel, match, match.team_a, match.team_b)

    await interaction.response.send_message(f"🥾 Player **<@{player_id}>** has been kicked.", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
    await on_match_action(match_id, interaction.channel)

async def ban_player_command(interaction: discord.Interaction, player_id:int, match_id: int):
    ban_player_from_match(player_id, match_id) # Add to ban list for this match
    await leave_match_command(interaction, match_id, player_id, True) # Kick player from lobby

    match = get_match_by_id(match_id)
    if match is None:
        return
    await refresh_match_in_lobby(interaction.channel, match, match.team_a, match.team_b)

    await interaction.response.send_message(f"⛔ Player **<@{player_id}>** has been banned.", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
    await on_match_action(match_id, interaction.channel)
    