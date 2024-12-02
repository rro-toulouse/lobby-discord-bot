# Discord Bot - Lobby and leaderboard manager

## Pre-requisities

### 1. Clone repository

```
git clone https://github.com/rro-toulouse/lobby-discord-bot.git
```

### 2. Setup python virtual env

```
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install discord.py
```

## Run 

### 1. Update Discord Tokens and IDs

In *bot.py*, replace :
- TOKEN with your discord server token.
- ALLOWED_CHANNEL_ID with your channel ID.

### 2. Launch bot

```
python bot.py
```
