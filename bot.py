import discord
import sqlite3
import os
from enum import Enum
from dotenv import load_dotenv
from discord.ext import commands
from discord.ui import Button, View

load_dotenv()
TOKEN = os.getenv("DISCORD_API_TOKEN")
ALLOWED_CHANNEL_ID = os.getenv("WAR_CHANNEL_ID")
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ELO 
STARTING_ELO = 1000

class Elo(Enum):
    REALISM_2V2 = 1
    REALISM = 2
    DEFAULT_2V2 = 3
    DEFAULT = 4
    NONE = 5

# Enum for match states
class MatchState(Enum):
    IN_CONSTRUCTION = "in_construction"
    IN_PROGRESS = "in_progress"
    DONE = "done"

# Enum for match states
class MatchState:
    IN_CONSTRUCTION = "in construction"
    IN_PROGRESS = "in progress"
    DONE = "done"

# Database connection
db_connection = sqlite3.connect(os.getenv("DATABASE_PATH"))
db_cursor = db_connection.cursor()

# Ensure the table exists
db_cursor.execute("""
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state TEXT NOT NULL,
    team_a_players TEXT NOT NULL,
    team_b_players TEXT NOT NULL,
    creator_id INTEGER NOT NULL,
    map_a TEXT,
    map_b TEXT,
    start_datetime TEXT,
    game_type TEXT NOT NULL,
    creation_datetime TEXT NOT NULL
)
""")
db_connection.commit()
db_cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    elo_realism INTEGER DEFAULT 1000,
    elo_realism_2v2 INTEGER DEFAULT 1000,
    elo_default INTEGER DEFAULT 1000,
    elo_default_2v2 INTEGER DEFAULT 1000, 
    created_at TEXT NOT NULL
)
""")
db_connection.commit()

# Define the view with buttons for the main menu
class MainMenuView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Buttons persist until explicitly removed

        # Add buttons to the view
        self.add_item(Button(label="Create Match", style=discord.ButtonStyle.primary, custom_id="create_match"))
        self.add_item(Button(label="Join Match", style=discord.ButtonStyle.success, custom_id="join_match"))
        self.add_item(Button(label="View Profile", style=discord.ButtonStyle.secondary, custom_id="view_profile"))
        self.add_item(Button(label="Help", style=discord.ButtonStyle.link, url="https://your-help-url.com"))  # Link button

# Define the match creation menu after clicking the "Create Match" button
class CreateMatchView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Keep buttons persistent
        # Buttons for selecting match type and size
        self.add_item(Button(label="Rea 2v2/3v3", style=discord.ButtonStyle.primary, custom_id="obj_realism_2v2"))
        self.add_item(Button(label="Realism", style=discord.ButtonStyle.primary, custom_id="obj_realism"))
        self.add_item(Button(label="Def 2v2/3v3", style=discord.ButtonStyle.primary, custom_id="obj_default_2v2"))
        self.add_item(Button(label="Default", style=discord.ButtonStyle.primary, custom_id="obj_default"))


# Function to add or update user in the database
def ensure_user_in_db(user: discord.User):
    db_cursor.execute("SELECT * FROM users WHERE id = ?", (user.id,))
    user_record = db_cursor.fetchone()

    if not user_record:
        # If user doesn't exist, insert them
        db_cursor.execute("""
        INSERT INTO users (id, username, elo, created_at)
        VALUES (?, ?, ?, ?)
        """, (user.id, user.name, STARTING_ELO, STARTING_ELO, STARTING_ELO, STARTING_ELO, datetime.now().isoformat()))
        db_connection.commit()
    else:
        # Update username in case it has changed
        db_cursor.execute("""
        UPDATE users SET username = ? WHERE id = ?
        """, (user.name, user.id))
        db_connection.commit()

# Fetch user ELO
def get_user_elo(user_id, elo_type):
    result = db_cursor.fetchone()

    # Filtering
    if elo_type == Elo.REALISM_2V2:
        db_cursor.execute("SELECT elo_realism_2v2 FROM users WHERE id = ?", (user_id,))
    elif elo_type == Elo.REALISM:
        db_cursor.execute("SELECT elo_realism FROM users WHERE id = ?", (user_id,))
    elif elo_type == Elo.DEFAULT_2V2:
        db_cursor.execute("SELECT elo_defaut_2v2 FROM users WHERE id = ?", (user_id,))
    elif elo_type == Elo.DEFAULT:
        db_cursor.execute("SELECT elo_defaut FROM users WHERE id = ?", (user_id,))
    else:
        return None
    result = db_cursor.fetchone()
    return result[0] if result else None

# Update user ELO
def update_user_elo(user_id, new_elo, elo_type):

    # Filtering
    if elo_type == Elo.REALISM_2V2:
        db_cursor.execute("""UPDATE users SET elo_realism_2v2 = ? WHERE id = ?""", (new_elo, user_id))
    elif elo_type == Elo.REALISM:
        db_cursor.execute("""UPDATE users SET elo_realism = ? WHERE id = ?""", (new_elo, user_id))
    elif elo_type == Elo.DEFAULT_2V2:
        db_cursor.execute("""UPDATE users SET elo_defaut_2v2 = ? WHERE id = ?""", (new_elo, user_id))
    elif elo_type == Elo.DEFAULT:
        db_cursor.execute("""UPDATE users SET elo_defaut = ? WHERE id = ?""", (new_elo, user_id))
    else:
        return
    db_connection.commit()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

    # Send the button to the specific channel
    channel = bot.get_channel(ALLOWED_CHANNEL_ID)
    if channel:
        await channel.send("Welcome to the Main Menu! Choose an option below:", view=MainMenuView())

@bot.event
async def on_interaction(interaction: discord.Interaction):
    # Check if this interaction comes from a button and get its custom_id
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get("custom_id")
        
        if custom_id == "synchronize_account":
            await interaction.response.send_message("You selected 'Create Match'. Starting the workflow...", ephemeral=True)
            # Add logic to handle the 'Create Match' workflow here

        elif custom_id == "create_match":
            await interaction.response.send_message("You selected 'Create Match'. Starting the workflow...", ephemeral=True)
            await interaction.followup.send("Select the match type:", view=CreateMatchView())

        elif custom_id == "join_match":
            await interaction.response.send_message("You selected 'Create Match'. Please select the match type and size.", ephemeral=True)
          
        elif custom_id == "view_profile":
            user_elo_realism_2v2 = get_user_elo(interaction.user.id, Elo.REALISM_2V2)
            user_elo_realism = get_user_elo(interaction.user.id, Elo.REALISM)
            user_elo_default_2v2 = get_user_elo(interaction.user.id, Elo.DEFAULT_2V2)
            user_elo_default = get_user_elo(interaction.user.id, Elo.DEFAULT)
            await interaction.response.send_message("You selected 'View Profile'. Retrieving your profile...\nYour Realism 2v2/3v3 ELO is " + str(user_elo_realism_2v2) + "\nYour Realism ELO is " + str(user_elo_realism) + "\nYour Default 2v2/3v3 ELO is " + str(user_elo_default_2v2) + "\nYour Default ELO is " + str(user_elo_default), ephemeral=True)
           
        elif custom_id.startswith("obj_"):
            # Handle selection for match type
            match_type = custom_id.replace("_", " ").title()
            # Insert match creation data into the database
            creator_id = interaction.user.id
            creation_datetime = datetime.now().isoformat()
            match_data = {
                "state": MatchState.IN_CONSTRUCTION,
                "team_a_players": json.dumps([creator_id]),
                "team_b_players": json.dumps([]),
                "creator_id": creator_id,
                "map_a": None,
                "map_b": None,
                "start_datetime": None,
                "game_type": game_type,
                "creation_datetime": creation_datetime
            }

            db_cursor.execute("""
            INSERT INTO matches (state, team_a_players, team_b_players, creator_id, map_a, map_b, start_datetime, game_type, creation_datetime)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match_data["state"],
                match_data["team_a_players"],
                match_data["team_b_players"],
                match_data["creator_id"],
                match_data["map_a"],
                match_data["map_b"],
                match_data["start_datetime"],
                match_data["game_type"],
                match_data["creation_datetime"]
            ))
            db_connection.commit()

            await interaction.response.send_message(f"Match created successfully! Game type: {game_type}. You have been added to Team A.", ephemeral=True)
        # No interaction handling required for the "Help" button as it's a link button

bot.run(TOKEN)
