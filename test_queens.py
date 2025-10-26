from src.envs.queens_env import QueensEnv, QueensAction

# Test the environment with level 1 (8x8)
env = QueensEnv()

# Reset with level 1
obs = env.reset(grid_size=8, level_id=1)
print("Initial board (8x8, level 1):")
for row in obs.board:
    print(row)
print("Grid size:", obs.board.__len__())
print("Legal actions count:", len(obs.legal_actions))
print("Regions:")
for row in obs.regions:
    print(row)

# Take an action, e.g., place queen at cell 0
action = QueensAction(cell_index=0, action_type=2)
obs = env.step(action)
print("After placing queen at 0:")
for row in obs.board:
    print(row)
print("Reward:", obs.reward)
print("Done:", obs.done)

env.close()
