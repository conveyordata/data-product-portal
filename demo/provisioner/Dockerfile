FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and MinIO client
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && wget -q https://dl.min.io/client/mc/release/linux-amd64/mc -O /usr/local/bin/mc \
    && chmod +x /usr/local/bin/mc

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY provisioner/ ./provisioner/

# Expose port
EXPOSE 8090

# Run the application
CMD ["uvicorn", "provisioner.main:app", "--host", "0.0.0.0", "--port", "8090", "--reload"]
