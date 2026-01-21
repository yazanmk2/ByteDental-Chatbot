#!/bin/bash
# Download Qwen2.5-3B-Instruct GGUF model for production use
# This script downloads the Q4_K_M quantized version for optimal CPU performance

set -e

MODEL_DIR="/opt/senior-dental-ai-chatbot/models"
MODEL_FILE="qwen2.5-3b-instruct-q4_k_m.gguf"
MODEL_URL="https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"

echo "================================================"
echo "Downloading Qwen2.5-3B-Instruct GGUF Model"
echo "================================================"

# Create models directory if it doesn't exist
mkdir -p "$MODEL_DIR"
cd "$MODEL_DIR"

# Check if model already exists
if [ -f "$MODEL_FILE" ]; then
    echo "Model already exists at: $MODEL_DIR/$MODEL_FILE"
    echo "File size: $(du -h $MODEL_FILE | cut -f1)"
    read -p "Do you want to re-download? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping download."
        exit 0
    fi
    rm "$MODEL_FILE"
fi

echo "Downloading model from Hugging Face..."
echo "Source: $MODEL_URL"
echo "Destination: $MODEL_DIR/$MODEL_FILE"
echo ""
echo "Note: This is a ~2GB download. Please be patient..."
echo ""

# Download with wget (shows progress)
if command -v wget &> /dev/null; then
    wget --progress=bar:force:noscroll -O "$MODEL_FILE" "$MODEL_URL"
# Fallback to curl
elif command -v curl &> /dev/null; then
    curl -L -o "$MODEL_FILE" --progress-bar "$MODEL_URL"
else
    echo "Error: Neither wget nor curl found. Please install one of them."
    exit 1
fi

# Verify download
if [ -f "$MODEL_FILE" ]; then
    FILE_SIZE=$(du -h "$MODEL_FILE" | cut -f1)
    echo ""
    echo "================================================"
    echo "Download completed successfully!"
    echo "================================================"
    echo "Model: $MODEL_FILE"
    echo "Size: $FILE_SIZE"
    echo "Location: $MODEL_DIR/$MODEL_FILE"
    echo ""
    echo "The model is ready for use."
else
    echo ""
    echo "Error: Download failed. Please check your internet connection and try again."
    exit 1
fi
