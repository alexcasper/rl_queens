FROM rocm/pytorch:latest

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    python3-pip \
    python3-dev \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    export PATH="$HOME/.cargo/bin:$PATH"

# Copy requirements first for better caching
COPY requirements.txt /app/
COPY pyproject.toml /app/
COPY src/ /app/src/

# Install Python dependencies (optimized for MI300X)
RUN pip3 install --no-cache-dir -r requirements.txt && \
    pip3 install --no-cache-dir \
    torch \
    torchvision \
    unsloth \
    transformers \
    trl \
    datasets \
    trackio \
    fastapi \
    uvicorn \
    requests \
    open_spiel \
    peft \
    accelerate \
    bitsandbytes

# Copy remaining project files
COPY . /app

# Create necessary directories
RUN mkdir -p /app/models /app/logs /app/output /app/cache /app/outputs_queens

# Set environment variables for ROCm and MI300X
ENV HIP_VISIBLE_DEVICES=0
ENV HSA_OVERRIDE_GFX_VERSION=11.0.0
ENV ROCM_PATH=/opt/rocm
ENV LD_LIBRARY_PATH=/opt/rocm/lib:$LD_LIBRARY_PATH
ENV PATH=/opt/rocm/bin:/usr/local/bin:$PATH

# Set Python environment
ENV PYTHONPATH=/app:$PYTHONPATH
ENV PYTHONUNBUFFERED=1

# Create a non-root user
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose ports for server and potential monitoring
EXPOSE 8003 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Default command (can be overridden in docker-compose)
CMD ["python3", "run_container_training.py"]
