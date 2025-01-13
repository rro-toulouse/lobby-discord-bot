import discord
from datetime import datetime
from database.db_manager import get_connection
from database.enums import Ladder
from models.Player import Player

STARTING_ELO = 1000

# Function to add or update     user in the database
def ensure_player_in_db(user: discord.User):
    db_connection = get_connection()
    db_cursor = db_connection.cursor()

    db_cursor.execute("SELECT * FROM players WHERE discord_id = ?", (user.id,))
    user_record = db_cursor.fetchone()

    if not user_record:
        # If user doesn't exist, insert them
        db_cursor.execute("""
        INSERT INTO players (discord_id, elo_realism, elo_default, created_at)
        VALUES (?, ?, ?, ?)
        """, (user.id, STARTING_ELO, STARTING_ELO, datetime.now().isoformat()))
        db_connection.commit()
    db_connection.close()

"""
Retrieve a player by their Discord ID from the database.

:param user_id: The Discord ID of the player to retrieve.
:return: The player record as a dictionary if found, otherwise None.
"""
def get_player_by_id(user_id) -> Player:

    db_connection = get_connection()
    db_cursor = db_connection.cursor()

    db_cursor.execute("SELECT * FROM players WHERE discord_id = ?", (user_id,))
    user_record = db_cursor.fetchone()
    db_connection.close()

    # Check if a user was found
    if user_record:
        # Return user data in a dictionary or any format you'd like
        match_data = Player.from_database(user_record)
        return match_data
    else:
        return None  # If no user found

# Fetch player ELO
def get_player_elo(user_id, elo_type):
    db_connection = get_connection()
    db_cursor = db_connection.cursor()

    result = db_cursor.fetchone()

    # Filtering
    if elo_type == Ladder.REALISM:
        db_cursor.execute("SELECT elo_realism FROM players WHERE discord_id = ?", (user_id,))
    elif elo_type == Ladder.DEFAULT:
        db_cursor.execute("SELECT elo_default FROM players WHERE discord_id = ?", (user_id,))
    else:
        return None
    result = db_cursor.fetchone()
    db_connection.close()
    return result[0] if result else None

# Update user ELO
def update_player_elo(user_id, new_elo, elo_type):
    db_connection = get_connection()
    db_cursor = db_connection.cursor()

    # Filtering
    if elo_type == Ladder.REALISM:
        db_cursor.execute("""UPDATE players SET elo_realism = ? WHERE discord_id = ?""", (new_elo, user_id))
    elif elo_type == Ladder.DEFAULT:
        db_cursor.execute("""UPDATE players SET elo_default = ? WHERE discord_id = ?""", (new_elo, user_id))
    else:
        return
    
    db_connection.commit()
    db_connection.close()
