from enum import Enum

class Ladder(Enum):
    REALISM = 1
    DEFAULT = 2
    NONE = 3

class MatchStep(Enum):
    IN_CONSTRUCTION = "in_construction"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class MatchIssue(Enum):
    MY_TEAM_WON = "my_team_won"
    OPPONENT_TEAM_WON = "opponent_team_won"
    DRAW = "draw"
    CANCEL = "cancel"
    NONE = "none"

class MatchRole(Enum):
    SPECTATOR = "spectator"
    PLAYER = "player"
    CREATOR = "creator"
    NONE = "none"
