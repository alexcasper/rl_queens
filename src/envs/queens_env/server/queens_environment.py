import uuid
import random
from typing import List, Optional
from src.envs.queens_env.models import QueensAction, QueensObservation, QueensState, CellState
from src.envs.queens_env.levels import get_level, get_random_level

class QueensEnvironment:
    def __init__(self, grid_size: int = 4, level_id: Optional[int] = None):
        self.grid_size = grid_size
        if level_id:
            level = get_level(level_id)
            if level and level['size'] == grid_size:
                self.regions = level['regions']
            else:
                self.regions = get_random_level(grid_size)['regions']
        else:
            self.regions = get_random_level(grid_size)['regions']
        self.board: List[List[int]] = [[CellState.EMPTY for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.step_count = 0
        self.episode_id = str(uuid.uuid4())

    def _generate_random_regions(self) -> List[List[int]]:
        # Generate random regions for a solvable Queens puzzle
        regions = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                regions[i][j] = random.randint(1, self.grid_size)
        return regions

    def reset(self) -> QueensObservation:
        self.board = [[CellState.EMPTY for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.step_count = 0
        self.episode_id = str(uuid.uuid4())
        return QueensObservation(
            board=self.board,
            regions=self.regions,
            legal_actions=self.get_legal_actions(),
            done=False
        )

    def step(self, action: QueensAction) -> QueensObservation:
        self.step_count += 1
        cell_index = action.cell_index
        row = cell_index // self.grid_size
        col = cell_index % self.grid_size
        action_type = action.action_type

        if action_type == 0:  # clear
            self.board[row][col] = CellState.EMPTY
        elif action_type == 1:  # mark
            if self.board[row][col] == CellState.EMPTY:
                self.board[row][col] = CellState.MARKED
        elif action_type == 2:  # place queen
            if self.board[row][col] == CellState.EMPTY and self.is_valid_placement(row, col):
                self.board[row][col] = CellState.QUEEN

        reward = self.calculate_reward()
        done = self.is_done()
        return QueensObservation(
            board=self.board,
            regions=self.regions,
            legal_actions=self.get_legal_actions(),
            done=done,
            reward=reward
        )

    def is_valid_placement(self, row: int, col: int) -> bool:
        # Check row, column, region
        for i in range(self.grid_size):
            if i != col and self.board[row][i] == CellState.QUEEN:
                return False
            if i != row and self.board[i][col] == CellState.QUEEN:
                return False
        region = self.regions[row][col]
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if (i != row or j != col) and self.regions[i][j] == region and self.board[i][j] == CellState.QUEEN:
                    return False
        # Check adjacent (including diagonally)
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = row + di, col + dj
                if 0 <= ni < self.grid_size and 0 <= nj < self.grid_size and self.board[ni][nj] == CellState.QUEEN:
                    return False
        return True

    def calculate_reward(self) -> float:
        queens = 0
        invalid = 0
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] == CellState.QUEEN:
                    queens += 1
                    if not self.is_valid_placement(i, j):
                        invalid += 1
        return queens - invalid * 2

    def is_done(self) -> bool:
        queens = []
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] == CellState.QUEEN:
                    queens.append((i, j))
        if len(queens) != self.grid_size:
            return False
        # Check no two in same row/col/region/adjacent
        rows = set()
        cols = set()
        regions = set()
        for i, j in queens:
            if i in rows or j in cols:
                return False
            rows.add(i)
            cols.add(j)
            region = self.regions[i][j]
            if region in regions:
                return False
            regions.add(region)
            # Check adjacent
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    ni, nj = i + di, j + dj
                    if 0 <= ni < self.grid_size and 0 <= nj < self.grid_size and (ni, nj) in queens:
                        return False
        return True

    def get_legal_actions(self) -> List[int]:
        actions = []
        for cell in range(self.grid_size * self.grid_size):
            row = cell // self.grid_size
            col = cell % self.grid_size
            for action_type in [0, 1, 2]:
                if (action_type == 0) or \
                   (action_type == 1 and self.board[row][col] == CellState.EMPTY) or \
                   (action_type == 2 and self.board[row][col] == CellState.EMPTY and self.is_valid_placement(row, col)):
                    actions.append(cell * 3 + action_type)
        return actions

    def state(self) -> QueensState:
        return QueensState(
            episode_id=self.episode_id,
            step_count=self.step_count,
            grid_size=self.grid_size
        )
