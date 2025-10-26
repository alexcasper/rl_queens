from fastapi import FastAPI, Query
from src.envs.queens_env.models import QueensAction, QueensObservation, QueensState
from src.envs.queens_env.server.queens_environment import QueensEnvironment
import json

app = FastAPI()

env = QueensEnvironment(grid_size=4)  # Default

@app.post("/reset")
async def reset(grid_size: int = Query(4, ge=4, le=12)):
    global env
    env = QueensEnvironment(grid_size=grid_size)
    obs = env.reset()
    return obs

@app.post("/step")
async def step(action: dict):
    action_obj = QueensAction(**action)
    obs = env.step(action_obj)
    return obs

@app.get("/state")
async def state():
    return env.state()

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
