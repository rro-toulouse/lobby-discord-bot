import discord
from datetime import datetime
from database.db_manager import get_connection
from database.models import Ladder

STARTING_ELO = 1000

# Function to add or update     user in the database
def ensure_user_in_db(user: discord.User):
    db_connection = get_connection()
    db_cursor = db_connection.cursor()

    db_cursor.execute("SELECT * FROM users WHERE id = ?", (user.id,))
    user_record = db_cursor.fetchone()

    if not user_record:
        # If user doesn't exist, insert them
        db_cursor.execute("""
        INSERT INTO users (id, username, elo_realism_2v2, elo_realism, elo_default_2v2, elo_default, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user.id, user.name, STARTING_ELO, STARTING_ELO, STARTING_ELO, STARTING_ELO, datetime.now().isoformat()))
        db_connection.commit()
    else:
        # Update username in case it has changed
        db_cursor.execute("""
        UPDATE users SET username = ? WHERE id = ?
        """, (user.name, user.id))
        db_connection.commit() 
    db_connection.close()

# Fetch user ELO
def get_user_elo(user_id, elo_type):
    db_connection = get_connection()
    db_cursor = db_connection.cursor()

    result = db_cursor.fetchone()

    # Filtering
    if elo_type == Ladder.REALISM_2V2:
        db_cursor.execute("SELECT elo_realism_2v2 FROM users WHERE id = ?", (user_id,))
    elif elo_type == Ladder.REALISM:
        db_cursor.execute("SELECT elo_realism FROM users WHERE id = ?", (user_id,))
    elif elo_type == Ladder.DEFAULT_2V2:
        db_cursor.execute("SELECT elo_default_2v2 FROM users WHERE id = ?", (user_id,))
    elif elo_type == Ladder.DEFAULT:
        db_cursor.execute("SELECT elo_default FROM users WHERE id = ?", (user_id,))
    else:
        return None
    result = db_cursor.fetchone()
    db_connection.close()
    return result[0] if result else None

# Update user ELO
def update_user_elo(user_id, new_elo, elo_type):
    db_connection = get_connection()
    db_cursor = db_connection.cursor()

    # Filtering
    if elo_type == Ladder.REALISM_2V2:
        db_cursor.execute("""UPDATE users SET elo_realism_2v2 = ? WHERE id = ?""", (new_elo, user_id))
    elif elo_type == Ladder.REALISM:
        db_cursor.execute("""UPDATE users SET elo_realism = ? WHERE id = ?""", (new_elo, user_id))
    elif elo_type == Ladder.DEFAULT_2V2:
        db_cursor.execute("""UPDATE users SET elo_default_2v2 = ? WHERE id = ?""", (new_elo, user_id))
    elif elo_type == Ladder.DEFAULT:
        db_cursor.execute("""UPDATE users SET elo_default = ? WHERE id = ?""", (new_elo, user_id))
    else:
        return
    
    db_connection.commit()
    db_connection.close()