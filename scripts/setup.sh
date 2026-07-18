#!/bin/bash
set -e

echo "=================================================="
echo "Edge Vision Precision Landing - Native SITL Setup"
echo "=================================================="

# Update and install OS dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv libgl1-mesa-glx libglib2.0-0 build-essential cmake tree

# Setup Python virtual environment
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment in $VENV_DIR..."
    python3 -m venv $VENV_DIR
fi

echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install numpy opencv-python onnxruntime pyyaml matplotlib pandas

echo "=================================================="
echo "Setup Complete! Run 'source venv/bin/activate' to start."
echo "=================================================="
