# Queens Game RL Training

This project implements a reinforcement learning backend for the LinkedIn Queens puzzle game using OpenEnv and GRPO training.

## Setup

1. **Environment Setup**:
   ```bash
   source .venv/bin/activate
   uv pip install unsloth transformers trl datasets trackio torch torchvision fastapi uvicorn requests open_spiel
   ```

2. **Start the Queens Environment Server**:
   ```bash
   python -m uvicorn src.envs.queens_env.server.app:app --host 0.0.0.0 --port 8003 --reload
   ```

3. **Test the Environment**:
   ```bash
   python test_queens.py
   python test_training.py
   ```

## Training

Run the GRPO training loop:

```bash
python train_queens.py
```

### Training Configuration

- **Model**: GPT-OSS 20B with 4-bit quantization
- **LoRA Rank**: 4
- **Sequence Length**: 768
- **Training Steps**: 600
- **Grid Sizes**: 4-12 (configurable)
- **Levels**: Supports existing LinkedIn levels and random generation

### Features

- ✅ Variable grid sizes (4x4 to 12x12)
- ✅ Load existing LinkedIn Queens levels
- ✅ Random level generator
- ✅ Full Queens game rules enforcement
- ✅ GRPO training with reward functions
- ✅ Server-ready for Ubuntu deployment
- ✅ MI300X GPU optimized

## Usage Examples

```python
from src.envs.queens_env import QueensEnv, QueensAction

# Use specific level
env = QueensEnv()
obs = env.reset(grid_size=8, level_id=1)

# Use random level
obs = env.reset(grid_size=10)

# Take actions
action = QueensAction(cell_index=0, action_type=2)
obs = env.step(action)
```

## Project Structure

```
src/envs/queens_env/
├── models.py          # Data models (Action, Observation, State)
├── client.py          # HTTP client for environment
├── server/
│   ├── app.py         # FastAPI server
│   └── queens_environment.py  # Core game logic
├── levels.py          # Level definitions and random generator
└── __init__.py        # Exports

train_queens.py        # Main training script
test_queens.py         # Environment tests
test_training.py       # Training setup tests
```

## Notes

- The server runs on port 8003 by default
- Training uses TrackIO for metrics visualization
- Models are saved in 16-bit format for efficiency
- All game rules are strictly enforced (row, column, region, adjacency)
- Supports both specific levels and procedural generation

## Performance

Optimized for MI300X GPU with:
- 4-bit model quantization
- Gradient checkpointing
- Efficient memory usage
- Batch size 1 with gradient accumulation
