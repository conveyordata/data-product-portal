FROM ghcr.io/quarto-dev/quarto:latest

WORKDIR /app

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     curl \
#     wget \
#     gdebi-core \
#     && rm -rf /var/lib/apt/lists/*

# # Install Quarto
# RUN wget https://github.com/quarto-dev/quarto-cli/releases/download/v1.4.549/quarto-1.4.549-linux-amd64.deb && \
#     gdebi --non-interactive quarto-1.4.549-linux-amd64.deb && \
#     rm quarto-1.4.549-linux-amd64.deb

# # Install Python packages commonly used in Quarto docs
# RUN pip install --no-cache-dir \
#     jupyter \
#     matplotlib \
#     pandas \
#     plotly \
#     duckdb

# Create directories
RUN mkdir -p /products /rendered

# Copy render script
COPY render_docs.sh /app/render_docs.sh
RUN chmod +x /app/render_docs.sh

# Expose port for preview server
EXPOSE 8888

CMD ["/app/render_docs.sh"]
