from dotenv import load_dotenv

load_dotenv()

import discord
import os
from database.db_manager import *
from discord.ext import commands
from view.match_creation_view import CreateMatchView
from view.main_menu_view import MainMenuView
from utils.match_utils import on_match_action
from database.enums import MatchIssue, MatchStep
from services.match_service import is_user_already_in_match, create_match, post_match_to_history_channel
from services.player_service import *
from services.lobby_service import add_match_to_lobby
from models.Match import Match
from database.constants import DELETE_MESSAGE_AFTER_IN_SEC

TOKEN = os.getenv("DISCORD_API_TOKEN")
MATCH_LOBBY_CHANNEL = os.getenv("MATCH_LOBBY_CHANNEL_ID")
HOW_TO_PLAY_CHANNEL = os.getenv("HOW_TO_PLAY_CHANNEL_ID")
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL_ID")
DISCORD_SERVER_ID = os.getenv("DISCORD_GUILD_ID")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Start Database
db_connection = get_connection()
db_cursor = db_connection.cursor()
create_tables(db_connection, db_cursor)

# Register the /start command
@bot.tree.command(name="start", description="Start the bot and display the main menu in DM")
async def start(interaction: discord.Interaction):    
    try:
        await interaction.user.send("Welcome to the Main Menu! Choose an option below:", view=MainMenuView())
        await interaction.response.send_message("Check your private messages for the Main Menu!", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
    except discord.Forbidden:
        await interaction.response.send_message("I couldn't send you a private message. Please enable direct messages from server members.", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)

# Sync the command tree
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

    try:
        await bot.tree.sync()
        print(f"Bot is ready and commands are synced as {bot.user}")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# Handle button interactions
@bot.event
async def on_interaction(interaction: discord.Interaction):
    # Check if this interaction comes from a button and get its custom_id
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get("custom_id")
        
        if custom_id == "synchronize_account":
            await interaction.response.send_message("You selected 'Create Match'. Starting the workflow...", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
            # Add logic to handle the 'Create Match' workflow here
        
        elif custom_id == "create_match":
            # Check if user is not in existing match in construction or in progress         
            already_playing = is_user_already_in_match(interaction.user.id)
            if already_playing:
                await interaction.response.send_message("❌ You are already in a match, please leave it before joining another.", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
            else:
                await interaction.response.send_message("You selected 'Create Match'. Starting the workflow...", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
                await interaction.user.send("Select the match type:", view=CreateMatchView())
          
        elif custom_id == "view_profile":  
            ensure_player_in_db(interaction.user)
            user_elo_realism = get_player_elo(interaction.user.id, Ladder.REALISM)
            user_elo_default = get_player_elo(interaction.user.id, Ladder.DEFAULT)
            await interaction.response.send_message("Your Realism ELO is " + str(user_elo_realism) + "\nYour Default ELO is " + str(user_elo_default), ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
           
        elif custom_id == "help":
            how_to_play_channel = bot.get_channel(int(HOW_TO_PLAY_CHANNEL))
            support_channel = bot.get_channel(int(SUPPORT_CHANNEL))
            if how_to_play_channel:
                await interaction.response.send_message(f":information_source: Open <#{how_to_play_channel.id}> to get help", ephemeral=True)
            elif support_channel:
                await interaction.response.send_message(f":information_source: Open a support ticket <#{support_channel.id}> here to get help", ephemeral=True)            
            else:
                await interaction.response.send_message(":information_source: Contact admins to get help", ephemeral=True)

        elif custom_id.startswith("obj_"):        
            ensure_player_in_db(interaction.user)
            already_playing = is_user_already_in_match(interaction.user.id)
            if already_playing:
                await interaction.response.send_message("❌ You are already in a match, please leave it before joining another.", ephemeral=True, delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
            
            else:
                game_type = Ladder.NONE
                if (custom_id == "obj_realism"):
                   game_type = Ladder.REALISM
                elif (custom_id == "obj_default"):
                    game_type = Ladder.DEFAULT
                    
                # Insert match creation data into the database
                creator_id = interaction.user.id
                team_a = []
                team_a.append(creator_id)
                match_id = create_match(Match(id=-1, creator_id=creator_id, team_a=team_a, game_type=game_type.value, state=MatchStep.IN_CONSTRUCTION))
                lobby_channel = bot.get_channel(int(MATCH_LOBBY_CHANNEL)) # Fetch the channel by ID
                if lobby_channel:
                    await add_match_to_lobby(
                        channel=lobby_channel,
                        match_id=match_id,
                        game_type=game_type,
                        creator_id=creator_id
                    )
                    await on_match_action(match_id, lobby_channel)
                    await interaction.response.send_message(f"✅ Match created and posted in <#{lobby_channel.id}>!", delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
                else:
                    print(f"Channel with ID {MATCH_LOBBY_CHANNEL} not found or bot cannot access it.")
                    await interaction.response.send_message("❌ Could not find the matches lobby channel.", delete_after=DELETE_MESSAGE_AFTER_IN_SEC)
                    
# Run the bot
bot.run(TOKEN)
