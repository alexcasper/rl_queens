#!/bin/bash
# Initial setup script for Queens Game RL Training
# For Ubuntu server with MI300X GPU

echo "=== Setting up Queens Game RL Training ==="

# Install Python and pip if not present
if ! command -v python3 &> /dev/null; then
    echo "Installing Python..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# Install uv package manager
if ! command -v uv &> /dev/null; then
    echo "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip and uv
pip install --upgrade pip uv

# Install PyTorch with CUDA support for MI300X
echo "Installing PyTorch with CUDA support..."
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Install other dependencies
echo "Installing dependencies..."
uv pip install unsloth transformers trl datasets trackio fastapi uvicorn requests open_spiel

echo "Setup completed!"
echo ""
echo "To run the training:"
echo "1. Start the environment server: python -m uvicorn src.envs.queens_env.server.app:app --host 0.0.0.0 --port 8003 --reload"
echo "2. In another terminal, run: python train_queens.py"
echo ""
echo "Or use the automated script: ./run_training.sh"
