CREATE TABLE matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state TEXT NOT NULL,
    team_a_players TEXT NOT NULL,  -- Store player IDs as a JSON string
    team_b_players TEXT NOT NULL,  -- Store player IDs as a JSON string
    creator_id INTEGER NOT NULL,
    map_a TEXT,
    map_b TEXT,
    start_datetime TEXT,
    game_type TEXT NOT NULL,
    creation_datetime TEXT NOT NULL
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY,                 -- Discord User ID
    username TEXT NOT NULL,                 -- User's Discord username
    elo_realism_2v2 INTEGER DEFAULT 1000,   -- ELO rating (default: 1000)
    elo_realism INTEGER DEFAULT 1000,       -- ELO rating (default: 1000)
    elo_default_2v2 INTEGER DEFAULT 1000,   -- ELO rating (default: 1000)
    elo_default INTEGER DEFAULT 1000,       -- ELO rating (default: 1000)
    created_at TEXT NOT NULL                -- Account creation timestamp
); 
