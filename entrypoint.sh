#!/usr/bin/env bash
set -e


# Load variables from .env if it exists
if [ -f "/app/.env" ]; then
    echo "Loading environment from .env..."
    set -a
    source /app/.env
    set +a
fi



# 1. Optional setup phase
# if [ ! -d "/app/models/llama-3.1-8b" ]; then
#     echo "Downloading Llama‑3.1‑8B model..."
#     hf download unsloth/Meta-Llama-3.1-8B \
#         --local-dir /app/models/llama-3.1-8b \
#         --token "${HF_TOKEN}"
# fi




# 2. Optional GPU-dependent build (only if you want)
if [ ! -f "/app/install_flash_attention.sh" ]; then
    echo "Building ROCm flash-attention..."
    /app/install_flash_attention.sh
fi

# 3. Finally run your Python training
exec python3 /app/train_queens.py