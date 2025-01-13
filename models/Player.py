from datetime import datetime

class Player:
    def __init__(self,
                discord_id: int = None, 
                elo_realism: int = None, 
                elo_default: int = None,
                created_at: datetime = None):
        self.discord_id = discord_id
        self.elo_realism = elo_realism
        self.elo_default = elo_default
        self.created_at = datetime.now().isoformat()

    """Convert the Player instance to a dictionary."""
    def to_dict(self):
        return {
            "discord_id": self.discord_id,
            "elo_realism": self.elo_realism,
            "elo_default": self.elo_default,
            "created_at": self.created_at.isoformat()
        }

    """Create a Player instance from a dictionary."""
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            discord_id=data["discord_id"],
            elo_realism=data.get("elo_realism", 0),
            elo_default=data.get("elo_default", 0),
            created_at=datetime.fromisoformat(data["created_at"])
        )
    
    """Create a Player instance from a database record."""
    def from_database(row: dict):
        if not row:
            return None
        
        return Player(
            discord_id=row[0],
            elo_realism=row[1],
            elo_default=row[2],
            created_at=row[3]
        )
