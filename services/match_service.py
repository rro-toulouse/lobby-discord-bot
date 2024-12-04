import json
from datetime import datetime
from database.Match import Match
from database.db_manager import get_connection
from database.models import MatchState

"""
Checks if a user is already in any team across active matches.
"""
def is_user_already_in_war(user_id):
    return False
    db_connection = get_connection()
    db_cursor = db_connection.cursor()

    user_id_str = str(user_id)  # Convert user_id to a string for JSON-like matching
    
    db_cursor.execute("""
    SELECT * FROM matches 
    WHERE 
        (team_a_players LIKE ? OR 
        team_b_players LIKE ?) AND
        (state LIKE ? OR
        state LIKE ?)
    """, (f'%{user_id_str}%', f'%{user_id_str}%', f'%{MatchState.IN_CONSTRUCTION.value}%', f'%{MatchState.IN_PROGRESS.value}%'))
    result = db_cursor.fetchone() is not None  # Return the first match found, if any
    db_connection.close()
    return result 

def get_lobby_matches():
    db_connection = get_connection()
    db_cursor = db_connection.cursor()

    db_cursor.execute("""
    SELECT * FROM matches
    WHERE state IN (?, ?)
    """, (MatchState.IN_CONSTRUCTION.value, MatchState.IN_PROGRESS.value))
    matches = db_cursor.fetchall()
    db_connection.close()
    return matches

"""
Creates a new match and adds the creator to Team A.
"""
def create_match(match: Match):
    db_connection = get_connection()
    db_cursor = db_connection.cursor()

    db_cursor.execute(
            """
            INSERT INTO matches (state, team_a_players, team_b_players, creator_id, map_a, map_b, start_datetime, game_type, creation_datetime)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (match.state.value,
            '['+','.join(map(str, match.team_a))+']',
            '['+','.join(map(str, match.team_b))+']',
            match.creator_id,
            match.map_a,
            match.map_b,
            match.start_datetime,
            match.game_type,
            match.creation_datetime)
        )
    db_connection.commit()
    db_connection.close()

    return db_cursor.lastrowid  # Return the ID of the newly created match

"""
Updates the state of a match by match ID.
"""
def update_match(match_id, state=None, team_a_players=None, team_b_players=None, map_a=None, map_b=None, start_datetime=None): 
    db_connection = get_connection()
    db_cursor = db_connection.cursor()
    
    # Build the update query dynamically
    updates = []
    params = []

    if state is not None:
        updates.append("state = ?")
        params.append(state)
    if team_a_players is not None:
        updates.append("team_a_players = ?")
        params.append(json.dumps(team_a_players))
    if team_b_players is not None:
        updates.append("team_b_players = ?")
        params.append(json.dumps(team_b_players))
    if map_a is not None:
        updates.append("map_a = ?")
        params.append(map_a)
    if map_b is not None:
        updates.append("map_b = ?")
        params.append(map_b)
    if start_datetime is not None:
        updates.append("start_datetime = ?")
        params.append(start_datetime)

    params.append(match_id)
    query = f"UPDATE matches SET {', '.join(updates)} WHERE id = ?"
    db_cursor.execute(query, params)
    db_connection.commit()
    db_connection.close()

def add_player_to_team(match_id, team, user_id):
    """
    Adds a player to a specified team in a match.
    """
    if team not in ['team_a', 'team_b']:
        raise ValueError("Team must be 'team_a' or 'team_b'.")

    db_connection = get_connection()
    db_cursor = db_connection.cursor()

    # Fetch the current team list
    db_cursor.execute(f"SELECT {team}_players FROM matches WHERE id = ?", (match_id,))
    team_players = db_cursor.fetchone()

    if not team_players:
        db_connection.close()
        raise ValueError("Match not found.")

    current_team = json.loads(team_players[0])

    if user_id in current_team:
        db_connection.close()
        raise ValueError("You are already in this match.")

    current_team.append(user_id)

    # Update the team in the database
    db_cursor.execute(f"""
    UPDATE matches
    SET {team}_players = ?
    WHERE id = ?
    """, (json.dumps(current_team), match_id))
    db_connection.commit()
    db_connection.close()

def switch_team(match_id, user_id):
    """
    Switches the user between Team A and Team B in a match.
    """
    db_connection = get_connection()
    db_cursor = db_connection.cursor()

    # Fetch the current team lists
    db_cursor.execute("SELECT team_a_players, team_b_players FROM matches WHERE id = ?", (match_id,))
    result = db_cursor.fetchone()

    if not result:
        db_connection.close()
        raise ValueError("Match not found.")

    team_a_players = json.loads(result[0])
    team_b_players = json.loads(result[1])

    # Check which team the user is currently in and switch
    if user_id in team_a_players:
        team_a_players.remove(user_id)
        team_b_players.append(user_id)
        new_team = "Team B"
    elif user_id in team_b_players:
        team_b_players.remove(user_id)
        team_a_players.append(user_id)
        new_team = "Team A"
    else:
        db_connection.close()
        raise ValueError("User is not in any team.")

    # Update the database
    db_cursor.execute("""
    UPDATE matches
    SET team_a_players = ?, team_b_players = ?
    WHERE id = ?
    """, (json.dumps(team_a_players), json.dumps(team_b_players), match_id))
    db_connection.commit()
    db_connection.close()

    return new_team

def get_match_by_id(match_id: int):
    # Connect to your SQLite database
    db_connection = get_connection()
    db_cursor = db_connection.cursor()

    # Query the database for the match by its ID
    db_cursor.execute("SELECT * FROM matches WHERE id = ?", (match_id,))
    match = db_cursor.fetchone()

    # Close the database connection
    db_connection.close()

    # Check if a match was found
    if match:
        # Return match data in a dictionary or any format you'd like
        match_data = Match.from_database(match)
        return match_data
    else:
        return None  # If no match found
    