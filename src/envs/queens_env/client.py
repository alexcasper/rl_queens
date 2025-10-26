import requests
from typing import Optional
from src.envs.queens_env.models import QueensAction, QueensObservation, QueensState

class QueensEnv:
    def __init__(self, base_url: str = "http://localhost:8003"):
        self.base_url = base_url

    def reset(self, grid_size: int = 4, level_id: int = None) -> QueensObservation:
        params = f"grid_size={grid_size}"
        if level_id:
            params += f"&level_id={level_id}"
        response = requests.post(f"{self.base_url}/reset?{params}")
        return QueensObservation(**response.json())

    def step(self, action: QueensAction) -> QueensObservation:
        response = requests.post(f"{self.base_url}/step", json=action.__dict__)
        return QueensObservation(**response.json())

    def state(self) -> QueensState:
        response = requests.get(f"{self.base_url}/state")
        return QueensState(**response.json())

    def close(self):
        # No specific cleanup needed for HTTP
        pass
