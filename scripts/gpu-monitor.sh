#!/bin/bash

# GPU Memory Monitor for 24GB VRAM
# Monitors VRAM usage and helps balance resources

set -e

INTERVAL=${1:-5}  # Monitor interval in seconds (default: 5s)
ALERT_THRESHOLD=${2:-90}  # Alert when VRAM usage exceeds this percentage

echo "==================================="
echo "GPU Memory Monitor (24GB VRAM)"
echo "==================================="
echo "Monitoring every ${INTERVAL}s"
echo "Alert threshold: ${ALERT_THRESHOLD}%"
echo ""

# Function to get GPU info
get_gpu_info() {
    if command -v nvidia-smi &> /dev/null; then
        nvidia-smi --query-gpu=index,name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu \
            --format=csv,noheader,nounits
    else
        echo "nvidia-smi not found. Please install NVIDIA drivers."
        exit 1
    fi
}

# Function to format bytes to GB
bytes_to_gb() {
    echo "scale=2; $1/1024" | bc
}

# Function to calculate percentage
calc_percentage() {
    echo "scale=2; ($1 / $2) * 100" | bc
}

# Monitor loop
while true; do
    clear
    echo "==================================="
    echo "GPU Status - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "==================================="
    echo ""
    
    # Get GPU info
    gpu_info=$(get_gpu_info)
    
    IFS=',' read -r gpu_id gpu_name total_mem used_mem free_mem gpu_util temp <<< "$gpu_info"
    
    # Calculate usage percentage
    usage_percent=$(calc_percentage "$used_mem" "$total_mem")
    free_percent=$(calc_percentage "$free_mem" "$total_mem")
    
    # Convert to GB
    total_gb=$(bytes_to_gb "$total_mem")
    used_gb=$(bytes_to_gb "$used_mem")
    free_gb=$(bytes_to_gb "$free_mem")
    
    echo "GPU #${gpu_id}: ${gpu_name}"
    echo "-----------------------------------"
    echo "Total VRAM:    ${total_gb} GB"
    echo "Used VRAM:     ${used_gb} GB (${usage_percent}%)"
    echo "Free VRAM:     ${free_gb} GB (${free_percent}%)"
    echo "GPU Usage:     ${gpu_util}%"
    echo "Temperature:   ${temp}°C"
    echo ""
    
    # Memory allocation breakdown (estimated)
    echo "==================================="
    echo "Estimated Memory Allocation"
    echo "==================================="
    
    # Calculate estimated allocations based on 24GB
    llm_alloc=$(echo "scale=2; $total_gb * 0.50" | bc)
    voice_alloc=$(echo "scale=2; $total_gb * 0.30" | bc)
    buffer_alloc=$(echo "scale=2; $total_gb * 0.20" | bc)
    
    echo "LLM Models:    ${llm_alloc} GB (50%)"
    echo "Voice Models:  ${voice_alloc} GB (30%)"
    echo "Buffer/Shared: ${buffer_alloc} GB (20%)"
    echo ""
    
    # Alert if usage is high
    if (( $(echo "$usage_percent > $ALERT_THRESHOLD" | bc -l) )); then
        echo "⚠️  WARNING: GPU memory usage is high!"
        echo "   Consider:"
        echo "   - Reducing batch size"
        echo "   - Using smaller models"
        echo "   - Clearing CUDA cache"
        echo ""
    fi
    
    # Check if near memory limits
    if (( $(echo "$free_gb < 2" | bc -l) )); then
        echo "⚠️  CRITICAL: Less than 2GB free VRAM!"
        echo "   System may experience OOM errors"
        echo ""
    fi
    
    # Show running processes using GPU
    echo "==================================="
    echo "GPU Processes"
    echo "==================================="
    nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader,nounits 2>/dev/null || echo "No processes found"
    echo ""
    
    echo "Press Ctrl+C to stop monitoring..."
    
    sleep "$INTERVAL"
done
