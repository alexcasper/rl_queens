FROM rocm/pytorch:latest

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git curl wget build-essential cmake \
    rocm-smi && \
    rm -rf /var/lib/apt/lists/*

# Create and activate venv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Ensure pip is up to date
RUN pip install --upgrade pip setuptools wheel

# Install core dependencies (with urllib3!)
RUN pip install --no-cache-dir \
    scipy pandas pyarrow \
    pydantic pyyaml jsonschema \
    ninja packaging psutil \
    urllib3 charset-normalizer certifi \
    requests httpx \
    fastapi python-multipart \
    uvicorn[standard] regex

# Hugging Face packages
RUN pip install --no-cache-dir \
    huggingface-hub safetensors tokenizers datasets hf_transfer "transformers==4.56.2" 

# Monitoring
RUN pip install --no-cache-dir wandb

# Tokenizer
RUN pip install --no-cache-dir sentencepiece protobuf

# ML packages with --no-deps
RUN pip install --no-deps \
    transformers trl peft accelerate 

RUN pip3 install accelerate einops tqdm

# Install bitsandbytes for ROCm (or skip if not needed)

RUN git clone -b rocm_enabled_multi_backend https://github.com/ROCm/bitsandbytes.git && \
    cd bitsandbytes && cmake -D BNB_ROCM_ARCH="gfx942" -DCOMPUTE_BACKEND=hip -S . && \
    make -j && pip install .


RUN pip install "torchao==0.13.0" 

RUN pip install "unsloth_zoo[base] @ git+https://github.com/unslothai/unsloth-zoo" \
        "unsloth[base] @ git+https://github.com/unslothai/unsloth" \
        git+https://github.com/triton-lang/triton.git@05b2c186c1b6c9a08375389d5efe9cb4c401c075#subdirectory=python/triton_kernels


# # Don't install unsloth if causing issues
# RUN pip install --no-deps  unsloth-zoo unsloth || echo "Warning: unsloth failed"

# Verify installation
RUN python3 -c "import torch; print(f'PyTorch: {torch.__version__}')" && \
    python3 -c "import urllib3; print('urllib3: OK')" && \
    python3 -c "import requests; print('requests: OK')"

# Copy application
COPY src/ /app/src/
COPY train_queens.py /app/

RUN mkdir -p /app/cache /app/logs /app/outputs_queens /app/models

# ROCm environment
ENV HIP_VISIBLE_DEVICES=0
ENV HSA_OVERRIDE_GFX_VERSION=11.0.0
ENV ROCM_PATH=/opt/rocm
ENV LD_LIBRARY_PATH=/opt/rocm/lib


COPY install_flash_attention.sh /app/install_flash_attention.sh
RUN chmod +x /app/install_flash_attention.sh

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY .env /app/.env

ENTRYPOINT ["/app/entrypoint.sh"]
