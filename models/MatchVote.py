from database.enums import MatchIssue

class MatchVote:
    def __init__(
        self,
        id: int,
        match_id: int,
        user_id: int,
        vote: MatchIssue
    ):
        self.id = id
        self.match_id = match_id
        self.user_id = user_id
        self.vote = vote

    def to_dict(self):
        """Convert the match vote object to a dictionary."""
        return {
            "match_id": self.match_id,
            "user_id": self.user_id,
            "vote": self.vote.value
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create a MatchVote instance from a dictionary."""
        return cls(
            match_id=data["match_id"],
            user_id=data["user_id"],
            vote=MatchIssue(data["vote"]),
        )
    
    def from_database(row: dict):
        """
        Converts a database row into a MatchVote model instance.
        
        Args:
            row (Dict[str, Any]): A dictionary representing a row from the matches table.
        
        Returns:
            MatchVote: A MatchVote model instance, or None if the row is None.
        """
        if not row:
            return None
        
        return MatchVote(
            id=row[0],
            match_id=int(row[1])
            user_id=int(row[2])
            vote=MatchIssue(row[3]),
        )

    def __str__(self):
        """String representation of the match."""
        return f"MatchVote {self.id}: Match ID: {str(self.match_id)} - User ID: {str(self.user_id)} - Vote: {self.vote.name}"