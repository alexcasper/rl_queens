#!/bin/bash
# Queens Game RL Training Runner
# For Ubuntu server with MI300X GPU

echo "=== Queens Game RL Training Setup ==="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Check GPU availability
echo "Checking GPU..."
if ! command -v nvidia-smi &> /dev/null; then
    echo "Warning: nvidia-smi not found. Make sure NVIDIA drivers are installed."
else
    nvidia-smi
fi

# Start the Queens environment server
echo "Starting Queens environment server..."
python -m uvicorn src.envs.queens_env.server.app:app --host 0.0.0.0 --port 8003 --reload &
SERVER_PID=$!

echo "Server started with PID: $SERVER_PID"
echo "Server available at: http://localhost:8003"
echo "Health check: http://localhost:8003/health"

# Wait a moment for server to start
sleep 3

# Test the environment
echo "Testing environment..."
python test_queens.py
if [ $? -ne 0 ]; then
    echo "Environment test failed!"
    kill $SERVER_PID
    exit 1
fi

python test_training.py
if [ $? -ne 0 ]; then
    echo "Training setup test failed!"
    kill $SERVER_PID
    exit 1
fi

echo "All tests passed! Ready for training."

# Ask user if they want to start training
read -p "Start training now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting training..."
    echo "This will take several hours. Monitor progress with TrackIO."
    echo "You can stop training with Ctrl+C"

    python train_queens.py

    echo "Training completed!"
else
    echo "Training not started. Server is still running."
    echo "To start training later, run: python train_queens.py"
    echo "To stop the server, run: kill $SERVER_PID"
fi
