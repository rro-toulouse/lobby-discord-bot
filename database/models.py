from enum import Enum

class Ladder(Enum):
    REALISM = 1
    DEFAULT = 2
    NONE = 3

# Enum for match states
class MatchState(Enum):
    IN_CONSTRUCTION = "in_construction"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class MatchResult(Enum):
    TEAM_A_WON = "team_a_won"
    TEAM_B_WON = "team_b_won"
    DRAW = "draw"
    CANCEL = "cancel"
    NONE = "none"
