#!/usr/bin/env python3
"""
Container entry point for Queens Game RL Training
Handles environment setup, server management, and training execution
"""

import os
import sys
import time
import subprocess
import signal
import threading
from pathlib import Path

def setup_environment():
    """Set up the container environment"""
    print("🏗️ Setting up Queens RL training environment...")

    # Ensure required directories exist
    directories = [
        "cache/transformers",
        "cache/huggingface",
        "outputs_queens",
        "models",
        "logs",
        "monitoring"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

def health_check():
    """Check if the Queens environment server is healthy"""
    try:
        import requests
        response = requests.get("http://localhost:8003/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def wait_for_server(timeout=60):
    """Wait for the server to be ready"""
    print("⏳ Waiting for Queens environment server...")
    start_time = time.time()

    while time.time() - start_time < timeout:
        if health_check():
            print("✅ Server is healthy!")
            return True
        time.sleep(2)

    print("❌ Server failed to start within timeout")
    return False

def test_environment():
    """Test the environment and training setup"""
    print("🧪 Testing environment...")

    try:
        # Add current directory and possible container path to sys.path
        import sys
        current_dir = os.getcwd()
        sys.path.insert(0, current_dir)
        if os.path.exists('/app'):
            sys.path.insert(0, '/app')

        # Also add src to path
        src_path = os.path.join(current_dir, 'src')
        sys.path.insert(0, src_path)

        from envs.queens_env import QueensEnv, QueensAction

        # Test basic functionality
        env = QueensEnv()
        obs = env.reset(grid_size=5)
        print(f"✓ Environment reset successful: {len(obs.board)}x5 grid")
        env.close()

        return True

    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python path: {sys.path[:3]}")  # Show first 3 paths
        return False

def run_training():
    """Run the main training loop"""
    print("🚀 Starting Queens RL training...")

    try:
        # Determine if we're in container (look for /app) or host system
        working_dir = "/app" if os.path.exists("/app") else os.getcwd()
        train_script = os.path.join(working_dir, "train_queens.py")

        if not os.path.exists(train_script):
            # Try relative to current script
            import sys
            script_dir = os.path.dirname(os.path.abspath(__file__))
            train_script = os.path.join(script_dir, "train_queens.py")

        print(f"Using training script: {train_script}")

        # Start training in subprocess to handle signals properly
        result = subprocess.run([
            "python3", train_script
        ], cwd=os.path.dirname(train_script) if os.path.exists(train_script) else working_dir)

        if result.returncode == 0:
            print("✅ Training completed successfully!")
        else:
            print(f"❌ Training failed with return code: {result.returncode}")

        return result.returncode

    except Exception as e:
        print(f"❌ Training failed with exception: {e}")
        return 1

def run_server():
    """Run the Queens environment server"""
    print("🌐 Starting Queens environment server...")
    return subprocess.Popen([
        "python3", "-m", "uvicorn",
        "src.envs.queens_env.server.app:app",
        "--host", "0.0.0.0",
        "--port", "8003",
        "--reload",
        "--log-level", "info"
    ], cwd=os.getcwd())

def main():
    """Main container entry point"""
    in_container = os.path.exists("/app")
    if in_container:
        print("👑 Queens Game RL Training Container Starting...")
    else:
        print("🏠 Queens Game RL Training Local Execution...")
        print("⚠️  Note: This script is designed for Docker containers.")
        print("   For local development, use: ./run_training.sh")

    print(f"Working directory: {os.getcwd()}")

    # Setup environment
    setup_environment()

    # Start server in background
    server_process = run_server()

    try:
        # Wait for server to be ready
        if not wait_for_server():
            print("❌ Server failed to start")
            return 1

        # Test environment
        if not test_environment():
            print("❌ Environment tests failed")
            return 1

        # Run training
        exit_code = run_training()
        return exit_code

    except KeyboardInterrupt:
        print("\n⏹️ Received interrupt signal")
        return 0

    finally:
        # Clean up server
        print("🧹 Cleaning up...")
        if server_process:
            server_process.terminate()
            try:
                server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                print("⚠️ Server didn't terminate gracefully, killing...")
                server_process.kill()

        print("👋 Container shutdown complete")

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
