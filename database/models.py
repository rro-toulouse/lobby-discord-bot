from enum import Enum

class Ladder(Enum):
    REALISM_2V2 = 1
    REALISM = 2
    DEFAULT_2V2 = 3
    DEFAULT = 4
    NONE = 5

# Enum for match states
class MatchState(Enum):
    IN_CONSTRUCTION = "in_construction"
    IN_PROGRESS = "in_progress"
    DONE = "done"
