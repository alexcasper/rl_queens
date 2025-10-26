#!/usr/bin/env python3
"""
Test script for Queens RL training setup
"""

import sys
sys.path.insert(0, 'src')

from envs.queens_env import QueensEnv, QueensAction

def test_environment():
    """Test the Queens environment"""
    print("Testing Queens environment...")

    env = QueensEnv()
    obs = env.reset(grid_size=5, level_id=1)

    print(f"Grid size: {len(obs.board)}")
    print(f"Regions shape: {len(obs.regions)}x{len(obs.regions[0])}")
    print(f"Legal actions: {len(obs.legal_actions)}")

    # Test a few actions
    for i in range(3):
        if obs.legal_actions:
            action_id = obs.legal_actions[0]
            cell_index = action_id // 3
            action_type = action_id % 3
            action = QueensAction(cell_index=cell_index, action_type=action_type)
            obs = env.step(action)
            print(f"Step {i+1}: Reward={obs.reward}, Done={obs.done}")

    env.close()
    print("Environment test passed!")

def test_level_loading():
    """Test loading different levels"""
    print("Testing level loading...")

    env = QueensEnv()

    # Test level 1
    obs = env.reset(grid_size=8, level_id=1)
    print(f"Level 1 regions sample: {obs.regions[0]}")

    # Test random level
    obs = env.reset(grid_size=6)
    print(f"Random 6x6 regions sample: {obs.regions[0]}")

    env.close()
    print("Level loading test passed!")

if __name__ == "__main__":
    test_environment()
    test_level_loading()
    print("All tests passed!")
