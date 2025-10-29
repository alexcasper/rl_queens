## Dependency Analysis for Queens Training Docker Setup

### Current Dockerfile Dependencies ✅
The following packages are already installed in the current Dockerfile:
- **Core ML/RL**: `transformers`, `trl`, `peft`, `accelerate`, `datasets`, `huggingface-hub`, `safetensors`, `tokenizers`
- **Unsloth**: `unsloth[colab-new]`, `unsloth-zoo`, `triton`
- **Quantization**: `bitsandbytes` (ROCm build)
- **Monitoring**: `wandb`
- **Other**: `scipy`, `pandas`, `pyarrow`, `pydantic`, `pyyaml`, `jsonschema`, `hf_transfer`

### Missing Dependencies 🔴
Based on code analysis, these packages are used but NOT installed in the Dockerfile:

#### 1. **Web/API Dependencies** (Required for Queens Environment Server)
```python
# Used in src/envs/queens_env/server/app.py
from fastapi import FastAPI, Query
# uvicorn server startup
uvicorn.run(app, host="0.0.0.0", port=8003)
```
**Missing packages:**
- `fastapi`
- `uvicorn[standard]`

#### 2. **HTTP Client Dependencies**
```python
# Used in src/envs/queens_env/client.py
import requests
# Used in train_queens.py
response = requests.get("http://localhost:8003/health", timeout=5)
```
**Missing packages:**
- `requests` (mentioned in requirements.txt but not in Dockerfile)

#### 3. **Data Processing Dependencies** (Used but may be cached in ROCm image)
```python
# Used in train_queens.py
from datasets import Dataset
import pandas, numpy, pyarrow
```
**Status**: These are in requirements.txt but need verification if already in ROCm base image

#### 4. **Training Tracking Dependency**
```python
# Used in train_queens.py
report_to="trackio"  # This might cause runtime issues
```
**Status**: `trackio` is referenced but might not be a real package

### Potential Runtime Issues 🚨

1. **Missing fastapi/uvicorn**: Will cause errors when:
   - Running the Queens environment server (`src/envs/queens_env/server/app.py`)
   - Any FastAPI-based functionality

2. **Missing requests**: Will cause errors when:
   - Queens environment client tries to communicate with server
   - Health checks in training script

3. **trackio issue**: Will cause errors when:
   - Training starts and tries to report to "trackio"

### Recommendations 📋

1. **Add to Dockerfile**:
   ```dockerfile
   RUN pip3 install --no-cache-dir \
       fastapi \
       uvicorn[standard] \
       requests
   ```

2. **Fix trackio issue** in `train_queens.py`:
   ```python
   # Change from:
   report_to="trackio"
   # To either:
   report_to="none"  # or
   report_to="wandb"  # if using wandb instead
   ```

3. **Verify pandas/numpy/pyarrow**: Check if ROCm base image already includes them
