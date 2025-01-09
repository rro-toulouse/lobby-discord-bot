from typing import List, Optional
from database.enums import MatchStep, Ladder, MatchIssue
from datetime import datetime

class Match:
    def __init__(
        self,
        id: int,
        creator_id: int,
        team_a: Optional[List[int]] = None,
        team_b: Optional[List[int]] = None,
        game_type: str = Ladder.NONE,
        state: MatchStep = MatchStep.IN_CONSTRUCTION,
        map_a: Optional[str] = None,
        map_b: Optional[str] = None,
        creation_datetime: Optional[datetime] = None,
        start_datetime: Optional[datetime] = None,
        result: Optional[MatchIssue] = MatchIssue.NONE,
        ready_players: Optional[List[int]] = None,
        ban_list: Optional[List[int]] = None,
    ):
        self.id = id
        self.creator_id = creator_id
        self.team_a = team_a if team_a is not None else []
        self.team_b = team_b if team_b is not None else []
        self.game_type = game_type
        self.state = state
        self.map_a = map_a
        self.map_b = map_b
        self.creation_datetime = datetime.now().isoformat()
        self.start_datetime = start_datetime 
        self.result = result
        self.ready_players = ready_players if ready_players is not None else set()
        self.ban_list = ban_list if ban_list is not None else []

    def to_dict(self):
        """Convert the match object to a dictionary."""
        return {
            "match_id": self.id,
            "creator_id": self.creator_id,
            "team_a": self.team_a,
            "team_b": self.team_b,
            "game_type": self.game_type,
            "state": self.state.value,
            "map_a": self.map_a,
            "map_b": self.map_b,
            "creation_datetime": self.start_datetime.isoformat(),
            "start_datetime": self.start_datetime.isoformat(),
            "result": self.result.value,
            "ready_players": self.ready_players,
            "ban_list": self.ban_list,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create a Match instance from a dictionary."""
        return cls(
            match_id=data["match_id"],
            creator_id=data["creator_id"],
            team_a=data.get("team_a", []),
            team_b=data.get("team_b", []),
            game_type=data["game_type"],
            state=MatchStep(data["state"]),
            map_a=data.get("map_a"),
            map_b=data.get("map_b"),
            creation_datetime=datetime.fromisoformat(data["creation_datetime"]),
            start_datetime=datetime.fromisoformat(data["start_datetime"]),
            result=MatchIssue(data["result"]),
            ready_players=data.get("ready_players", []),
            ban_list=data.get("ban_list", []),
        )
    
    def from_database(row: dict):
        """
        Converts a database row into a Match model instance.
        
        Args:
            row (Dict[str, Any]): A dictionary representing a row from the matches table.
        
        Returns:
            Match: A Match model instance, or None if the row is None.
        """
        if not row:
            return None
        
        return Match(
            id=row[0],
            creator_id=row[4],
            team_a=[int(player_id) for player_id in row[2][1:-1].split(",")] if row[2][1:-1] else [],
            team_b=[int(player_id) for player_id in row[3][1:-1].split(",")] if row[3][1:-1] else [],
            game_type=row[8],
            state=MatchStep(row[1]),
            map_a=row[5],
            map_b=row[6],
            creation_datetime=datetime.fromisoformat(row[9]) if row[9] else None,
            start_datetime=datetime.fromisoformat(row[7]) if row[7] else None,
            result=MatchIssue(row[10]),
            ready_players = [int(player_id) for player_id in row[11][1:-1].split(",")] if row[11][1:-1] else [],
            ban_list = [int(player_id) for player_id in row[12][1:-1].split(",")] if row[12][1:-1] else []
        )

    def __str__(self):
        """String representation of the match."""
        return f"Match {self.id}: {self.game_type} - State: {self.state.name} - Team A: {len(self.team_a)} vs Team B: {len(self.team_b)} - Result: {self.result.name}"