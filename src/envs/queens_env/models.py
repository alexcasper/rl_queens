from dataclasses import dataclass
from typing import List, Optional
from enum import IntEnum

class CellState(IntEnum):
    EMPTY = 0
    MARKED = 1
    QUEEN = 2

@dataclass
class QueensAction:
    cell_index: int  # 0 to grid_size*grid_size - 1
    action_type: int  # 0: clear, 1: mark, 2: place queen

@dataclass
class QueensObservation:
    board: List[List[int]]  # 2D list of CellState
    regions: List[List[int]]  # 2D list of region IDs
    legal_actions: List[int]  # list of valid action indices
    done: bool
    reward: Optional[float] = None

@dataclass
class QueensState:
    episode_id: str
    step_count: int
    grid_size: int
