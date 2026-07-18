# Dockerfile for Edge Vision Precision Landing - CPU Replay
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    libgl1-mesa-glx libglib2.0-0 \
    build-essential cmake \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
RUN pip3 install --no-cache-dir numpy opencv-python onnxruntime pyyaml matplotlib pandas

# Default execution script will be mapped via docker-compose
CMD ["bash"]
