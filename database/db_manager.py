
import sqlite3
import os
from dotenv import load_dotenv

# Returns db cursor
def get_connection():
    # Database connection
    return sqlite3.connect(os.getenv("DATABASE_PATH"))

def create_tables(db_connection, db_cursor):
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
        game_type INTEGER NOT NULL,
        creation_datetime TEXT NOT NULL,
        result TEXT NOT NULL,
        ready_players TEXT NOT NULL,
        ban_list TEXT NOT NULL,
        last_action DATETIME,
        team_a_points INTEGER NOT NULL,
        team_b_points INTEGER NOT NULL,
        team_a_elo INTEGER NOT NULL,
        team_b_elo INTEGER NOT NULL
    )
    """)
    db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        discord_id INTEGER PRIMARY KEY,
        elo_realism INTEGER DEFAULT 1000,
        elo_default INTEGER DEFAULT 1000,
        created_at TEXT NOT NULL
    )
    """)
    db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS match_votes (
        id INTEGER PRIMARY KEY,
        match_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        vote TEXT NOT NULL
    )
    """)

    # TODO replace user_ with player_

    db_connection.commit()
    db_connection.close()