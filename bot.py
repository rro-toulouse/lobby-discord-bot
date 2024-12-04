import discord
import os
import ast
from database.db_manager import *
from discord.ext import commands
from discord.ui import Button, View
from view.match_creation import CreateMatchView
from view.main_menu import MainMenuView
from database.models import MatchState
from services.match_service import get_match_by_id, is_user_already_in_war, get_lobby_matches, create_match, add_player_to_team
from services.user_service import *
from database.Match import Match

TOKEN = os.getenv("DISCORD_API_TOKEN")
WARS_LOBBY_CHANNEL = os.getenv("WAR_LOBBY_CHANNEL_ID")
DISCORD_SERVER_ID = os.getenv("DISCORD_GUILD_ID")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Store the message object globally for later editing
posted_message = None

# Start Database
db_connection = get_connection()
db_cursor = db_connection.cursor()
create_tables(db_connection, db_cursor)

class MatchJoinButton(Button):
    def __init__(self, match_id):
        super().__init__(label="Join Match", style=discord.ButtonStyle.green)
        self.match_id = match_id

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        try:
            # Add the user to Team A or Team B
            add_player_to_team(match_id=self.match_id, team="team_a", user_id=user_id)
            await interaction.response.send_message(f"✅ You have joined the match!", ephemeral=True)
        except ValueError as e:
            await interaction.response.send_message(f"❌ {str(e)}", ephemeral=True)

async def get_team_names(team_ids):
    team_names = []
    for player_id in team_ids:
        try:
            # Retrieve the member from the API
           # member = bot.get_user(player_id)
            member = bot.fetch_user(player_id)
            if member is not None:
                team_names.append(member.display_name)
            else:
                print(f"Player id {player_id} (Not Found)")
        except discord.NotFound:
            # Member is not found, handle accordingly (e.g., player left server)
            team_names.append(f"Player {player_id} (Not Found)")
    return team_names

async def post_match_to_lobby(channel: discord.TextChannel, match_id, game_type, creator_name, team_a, team_b):
    """
    Posts match details in the lobby channel with a "Join Match" button.
    """
    # Fetch player names for Team A and Team B
    team_a_names = await get_team_names(team_a)
    team_b_names = await get_team_names(team_b)

    description = f"Game Type: **{game_type}**\n"
    description += f"Created by: **{creator_name}**\n"
    description += f"**Team A:** {', '.join(team_a_names)}\n"
    description += f"**Team B:** {', '.join(team_b_names)}"
    embed = discord.Embed(
        title="New Match Created!",
        description=description,
        color=discord.Color.blue()
    )
    view = View()
    view.add_item(MatchJoinButton(match_id))

    global posted_message
    if not posted_message:
        posted_message = await channel.send(embed=embed, view=view)
    else:
        await posted_message.edit(embed=embed)

        
# Register the /start command
@bot.tree.command(name="start", description="Start the bot and display the main menu in DM")
async def start(interaction: discord.Interaction):
    ensure_user_in_db(interaction.user)
    
    try:
        await interaction.user.send("Welcome to the Main Menu! Choose an option below:", view=MainMenuView())
        await interaction.response.send_message("Check your private messages for the Main Menu!", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("I couldn't send you a private message. Please enable direct messages from server members.", ephemeral=True)

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
            await interaction.response.send_message("You selected 'Create Match'. Starting the workflow...", ephemeral=True)
            # Add logic to handle the 'Create Match' workflow here

        elif custom_id == "create_match":
            # Check if user is not in existing war in construction or in progress
            already_playing = is_user_already_in_war(interaction.user.id)
            if already_playing:
                await interaction.response.send_message("You are already in a war, please leave it before joining another. TODO Add 'Leave War' button", ephemeral=True)
            else:
                await interaction.user.send("Select the match type:", view=CreateMatchView())
          
        elif custom_id == "view_profile":
            user_elo_realism_2v2 = get_user_elo(interaction.user.id, Ladder.REALISM_2V2)
            user_elo_realism = get_user_elo(interaction.user.id, Ladder.REALISM)
            user_elo_default_2v2 = get_user_elo(interaction.user.id, Ladder.DEFAULT_2V2)
            user_elo_default = get_user_elo(interaction.user.id, Ladder.DEFAULT)
            await interaction.response.send_message("You selected 'View Profile'. Retrieving your profile...\nYour Realism 2v2/3v3 ELO is " + str(user_elo_realism_2v2) + "\nYour Realism ELO is " + str(user_elo_realism) + "\nYour Default 2v2/3v3 ELO is " + str(user_elo_default_2v2) + "\nYour Default ELO is " + str(user_elo_default), ephemeral=True)
           
        elif custom_id.startswith("obj_"):
            already_playing = is_user_already_in_war(interaction.user.id)
            if already_playing:
                await interaction.response.send_message("You are already in a war, please leave it before joining another. TODO Add 'Leave War' button", ephemeral=True)
            
            else:
                game_type = Ladder.NONE
                if (custom_id == "obj_realism_2v2"):
                    game_type = Ladder.REALISM_2V2
                elif (custom_id == "obj_realism"):
                   game_type = Ladder.REALISM
                elif (custom_id == "obj_default_2v2"):
                    game_type = Ladder.DEFAULT_2V2
                elif (custom_id == "obj_default"):
                    game_type = Ladder.DEFAULT
                    
                # Insert match creation data into the database
                creator_id = interaction.user.id
                team_a = []
                team_b = []
                team_a.append(creator_id)
                match_id = create_match(Match(match_id=-1, creator_id=creator_id, team_a=team_a, game_type=game_type.value, state=MatchState.IN_CONSTRUCTION))
                lobby_channel = bot.get_channel(1313453546670260244)  # Fetch the channel by ID
                if lobby_channel:
                    # Fetch player names for Team A and Team B
                    #match = get_match_by_id(match_id)
                   
                    await post_match_to_lobby(
                        channel=lobby_channel,
                        match_id=match_id,
                        game_type=game_type,
                        creator_name=interaction.user.display_name,
                        team_a=team_a,
                        team_b=team_b
                    )
                    await interaction.response.send_message(f"✅ Match created and posted in #{lobby_channel.name}!")
                else:
                    print(f"Channel with ID {1313453546670260244} not found or bot cannot access it.")
                    await interaction.response.send_message("❌ Could not find the #wars-lobby channel.")
                    
# Run the bot
bot.run(TOKEN)
