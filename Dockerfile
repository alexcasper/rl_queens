FROM rocm/vllm:latest
# That's it - nothing else!
WORKDIR /app

RUN pip3 install --no-cache-dir \
    scipy \
    pandas \
    pyarrow \
    pydantic \
    pyyaml \
    jsonschema \
    datasets \
    huggingface-hub \
    safetensors \
    tokenizers 


# Install torch-dependent packages with --no-deps
RUN pip3 install --no-deps --no-cache-dir \
    transformers \
    trl \
    peft \
    accelerate \
    langchain \
    langchain-openai \
    hf_transfer \
    trackio \ gradio \ gradio-client \ aiofiles \ safehttpx \ orjson


RUN git clone -b rocm_enabled_multi_backend https://github.com/ROCm/bitsandbytes.git && \
    cd bitsandbytes && cmake -D BNB_ROCM_ARCH="gfx942" -DCOMPUTE_BACKEND=hip -S . && \
    make -j && pip install .


# Install unsloth with --no-deps
RUN pip3 install "unsloth_zoo[base] @ git+https://github.com/unslothai/unsloth-zoo" \
  "unsloth[base] @ git+https://github.com/unslothai/unsloth" 

    
RUN pip3 install git+https://github.com/triton-lang/triton.git@05b2c186c1b6c9a08375389d5efe9cb4c401c075#subdirectory=python/triton_kernels
# Verify torch is still ROCm version
RUN python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'ROCm available: {torch.cuda.is_available()}')"


# Copy project files
COPY . /app


# Create necessary directories
RUN mkdir -p /app/models /app/model_checkpoints /app/model_artifacts /app/logs /app/outputs_queens /app/cache /app/cache/huggingface

# Set environment variables for ROCm
ENV HIP_VISIBLE_DEVICES=0
ENV HSA_OVERRIDE_GFX_VERSION=9.4.2
ENV ROCM_PATH=/opt/rocm
ENV PATH=/opt/rocm/bin:$PATH
ENV HIP_LAUNCH_BLOCKING=1  
# For better error messages

# Set HuggingFace cache
ENV HF_HOME=/app/cache/huggingface
ENV HF_HUB_ENABLE_HF_TRANSFER=1

CMD ["python3", "train_queens.py"]
