# Use Python 3.10 as base, then install code-server
FROM python:3.10-slim

USER root

# Install system dependencies and code-server
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    sudo && \
    rm -rf /var/lib/apt/lists/*

# Install code-server
RUN curl -fsSL https://code-server.dev/install.sh | sh

# Create coder user
RUN useradd -m -s /bin/bash coder && \
    echo "coder ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/nopasswd

# Install Python packages needed for SQLMesh data products
RUN pip install --no-cache-dir \
    sqlmesh[duckdb] \
    pandas \
    numpy \
    duckdb \
    polars \
    pyreadstat \
    python-dotenv \
    jupyterlab \
    ipython \
    boto3

# Switch to coder user
USER coder

# Install Python VS Code extension
RUN code-server --install-extension ms-python.python

# Set working directory
WORKDIR /home/coder
