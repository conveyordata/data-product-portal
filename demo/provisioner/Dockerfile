FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY provisioner/ ./provisioner/

# Expose port
EXPOSE 8090

# Run the application
CMD ["uvicorn", "provisioner.main:app", "--host", "0.0.0.0", "--port", "8090", "--reload"]
