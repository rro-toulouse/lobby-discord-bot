import discord
from discord import Embed

from database.enums import Ladder, MatchIssue
from models.Match import Match

class MatchHistoryEmbed(Embed):
    description = ""
    
    def __init__(self, match: Match):
        super().__init__()
        
        self.title="New match played"
        self.color=discord.Color.blue()

        match_result = MatchIssue.NONE
        if match.result == MatchIssue.TEAM_A_WON:
            match_result = "Team 🅰️ Won"
        elif match.result  == MatchIssue.TEAM_B_WON:
            match_result = "Team 🅱️ Won"
        elif match.result  ==  MatchIssue.DRAW:
            match_result = "🆎 Draw"
        elif match.result  ==  MatchIssue.CANCEL:
            match_result = "❌ Canceled"
        
        displayed_game_type = ""
        # TODO Add link to leaderboard channel for both Realism and Default
        if match.game_type == Ladder.REALISM.value:
            displayed_game_type = "Realism"
        elif match.game_type == Ladder.DEFAULT.value:
            displayed_game_type = "Default"
        
        self.description = f"🔫 {displayed_game_type}\n"
        self.description += f"📅 {match.start_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n"
        self.description += f"**{match_result}**\n\n"

        self.description += "🅰️ "
        if match.result != MatchIssue.CANCEL:
            self.description += f"**{match.team_a_elo}** points\n"
            self.description += f"**{'🟢 +' if match.team_a_points >= 0 else '🔴 '}{match.team_a_points}** points\n"
        for player in match.team_a:
            self.description += f"<@{player}> "
        self.description += "\n\n"

        self.description += "🅱 "
        if match.result != MatchIssue.CANCEL:
            self.description += f"**{match.team_b_elo}** points\n"
            self.description += f"**{'🟢 +' if match.team_b_points >= 0 else '🔴 '}{match.team_b_points}** points\n"
        for player in match.team_b:
            self.description += f"<@{player}> "
        self.description += "\n"

        