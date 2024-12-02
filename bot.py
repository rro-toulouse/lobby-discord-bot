import discord
import json
from enum import Enum
from discord.ext import commands
from discord.ui import Button, View

TOKEN = 'YOUR_DISCORD_TOKEN_HERE'
ALLOWED_CHANNEL_ID = YOUR_CHANNEL_ID_HERE  # Replace with your channel ID
USER_DATA_FILE = "./user_data.json"
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
        self.add_item(Button(label="Objective Realism 2v2/3v3", style=discord.ButtonStyle.primary, custom_id="obj_realism_2v2"))
        self.add_item(Button(label="Objective Realism", style=discord.ButtonStyle.primary, custom_id="obj_realism"))
        self.add_item(Button(label="Objective Default 2v2/3v3", style=discord.ButtonStyle.primary, custom_id="obj_default_2v2"))
        self.add_item(Button(label="Objective Default", style=discord.ButtonStyle.primary, custom_id="obj_default"))

# Get Elo value for a specific user
def get_elo(user_id, elo_type = Elo.NONE):
    user_data = load_user_data()
    elo_realism_2v2 = user_data.get(str(user_id), {}).get("elo_realism_2v2")
    elo_realism = user_data.get(str(user_id), {}).get("elo_realism")
    elo_default_2v2 = user_data.get(str(user_id), {}).get("elo_default_2v2")
    elo_default = user_data.get(str(user_id), {}).get("elo_default")

    # If ELO doesn't exist, create it
    if elo_realism_2v2 == None:
        elo_realism_2v2 = STARTING_ELO
        update_elo(user_id, STARTING_ELO)
    if elo_realism == None:
        elo_realism = STARTING_ELO
        update_elo(user_id, STARTING_ELO)
    if elo_default_2v2 == None:
        elo_default_2v2 = STARTING_ELO
        update_elo(user_id, STARTING_ELO)
    if elo_default == None:
        elo_default = STARTING_ELO
        update_elo(user_id, STARTING_ELO)

    # Filtering
    if elo_type == Elo.REALISM_2V2:
        return elo_realism_2v2
    elif elo_type == Elo.REALISM:
        return elo_realism
    if elo_type == Elo.DEFAULT_2V2:
        return elo_default_2v2
    if elo_type == Elo.DEFAULT:
        return elo_default
    else:
        return elo_realism_2v2, elo_realism, elo_default_2v2, elo_default 

# Update Elo value for a specific user
def update_elo(user_id, new_elo, elo_type = Elo.NONE):
    user_data = load_user_data()
    if str(user_id) not in user_data:
        user_data[str(user_id)] = {}
    
    # Filtering
    if elo_type == Elo.REALISM_2V2:
        user_data[str(user_id)]["elo_realism_2v2"] = new_elo
    elif elo_type == Elo.REALISM:
        user_data[str(user_id)]["elo_realism"] = new_elo
    if elo_type == Elo.DEFAULT_2V2:
        user_data[str(user_id)]["elo_default_2v2"] = new_elo
    if elo_type == Elo.DEFAULT:
        user_data[str(user_id)]["elo_default"] = new_elo
    else:
        user_data[str(user_id)]["elo_realism_2v2"] = new_elo
        user_data[str(user_id)]["elo_realism"] = new_elo
        user_data[str(user_id)]["elo_default_2v2"] = new_elo
        user_data[str(user_id)]["elo_default"] = new_elo
    
    save_user_data(user_data)

# Load user data from the JSON file
def load_user_data():
    try:
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save user data to the JSON file
def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

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
            user_elo_realism_2v2, user_elo_realism, user_elo_default, user_elo_default_2v2 = get_elo(interaction.user.id)
            await interaction.response.send_message("You selected 'View Profile'. Retrieving your profile...\nYour Realism 2v2/3v3 ELO is " + str(user_elo_realism_2v2) + "\nYour Realism ELO is " + str(user_elo_realism) + "\nYour Default 2v2/3v3 ELO is " + str(user_elo_default_2v2) + "\nYour Default ELO is " + str(user_elo_default), ephemeral=True)
           
        elif custom_id.startswith("obj_"):
            # Handle selection for match type
            match_type = custom_id.replace("_", " ").title()
            await interaction.response.send_message(f"You selected {match_type}. The match creation process will now continue...", ephemeral=True)
            # Add logic to handle match creation based on the selected match type here

        # No interaction handling required for the "Help" button as it's a link button

bot.run(TOKEN)
