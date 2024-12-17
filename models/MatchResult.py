from database.enums import MatchIssue

class MatchResult:
    def __init__(
        self,
        id: int,
        match_id: int,
        user_id: int,
        result: MatchIssue
    ):
        self.id = id
        self.match_id = match_id
        self.user_id = user_id
        self.result = result

    def to_dict(self):
        """Convert the match result object to a dictionary."""
        return {
            "match_id": self.match_id,
            "user_id": self.user_id,
            "result": self.result.value
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create a MatchResult instance from a dictionary."""
        return cls(
            match_id=data["match_id"],
            user_id=data["user_id"],
            result=MatchIssue(data["result"]),
        )
    
    def from_database(row: dict):
        """
        Converts a database row into a MatchResult model instance.
        
        Args:
            row (Dict[str, Any]): A dictionary representing a row from the matches table.
        
        Returns:
            MatchResult: A MatchResult model instance, or None if the row is None.
        """
        if not row:
            return None
        
        return MatchResult(
            id=row[0],
            match_id=int(row[1])
            user_id=int(row[2])
            result=MatchIssue(row[3]),
        )

    def __str__(self):
        """String representation of the match."""
        return f"MatchResult {self.id}: Match ID: {str(self.match_id)} - User ID: {str(self.user_id)} - Result: {self.result.name}"