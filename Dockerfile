FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for llama.cpp
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    curl \
    wget \
    git \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies including llama-cpp-python
# Build llama-cpp-python with OpenBLAS for ARM optimization
RUN CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" \
    pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p logs models

# Download Mini Orca quantized model if not present
RUN if [ ! -f models/mini-orca-small-q4_k_m.gguf ]; then \
    echo "Model will be downloaded on first run or mount from host"; \
    fi

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
