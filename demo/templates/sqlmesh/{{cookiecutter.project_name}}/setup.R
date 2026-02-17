#!/usr/bin/env Rscript
#' Setup R Environment for {{ cookiecutter.project_name }}
#'
#' This script sets up your R environment with required packages
#' and S3 configuration for working with this data product.
#'
#' Run this script once when you first open the project:
#'   source("setup.R")

cat("🚀 Setting up R environment for {{ cookiecutter.project_name }}\n")
cat("=================================================================\n\n")

# Install required packages if not already installed
required_packages <- c(
  "aws.s3",       # S3 access
  "arrow",        # Parquet file reading
  "duckdb",       # In-memory SQL analytics
  "dplyr",        # Data manipulation
  "readr",        # CSV reading
  "dotenv"        # .env file loading
)

cat("📦 Checking required packages...\n")
for (pkg in required_packages) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    cat(sprintf("   Installing %s...\n", pkg))
    install.packages(pkg, repos = "https://cloud.r-project.org/", quiet = TRUE)
  } else {
    cat(sprintf("   ✓ %s\n", pkg))
  }
}

# Load environment variables from .env
cat("\n🔧 Loading environment configuration...\n")
if (file.exists(".env")) {
  library(dotenv)
  load_dot_env()
  cat("   ✓ Loaded .env file\n")
} else {
  cat("   ⚠️  No .env file found - using defaults\n")
}

# Configure AWS S3 settings
Sys.setenv(
  "AWS_S3_ENDPOINT" = Sys.getenv("S3_ENDPOINT_HOST", "rustfs"),
  "AWS_ACCESS_KEY_ID" = Sys.getenv("S3_ACCESS_KEY", "minioadmin"),
  "AWS_SECRET_ACCESS_KEY" = Sys.getenv("S3_SECRET_KEY", "minioadmin"),
  "AWS_DEFAULT_REGION" = "us-east-1"
)

cat("\n🗄️  S3 Configuration:\n")
cat(sprintf("   Endpoint: %s:9000\n", Sys.getenv("AWS_S3_ENDPOINT")))
cat(sprintf("   Bucket:   %s\n", Sys.getenv("S3_BUCKET", "data-products")))
cat(sprintf("   Prefix:   %s\n", Sys.getenv("S3_PREFIX", "{{ cookiecutter.project_name }}")))

cat("\n✅ Setup complete!\n\n")
cat("📚 Next steps:\n")
cat("   1. Run load_data.R to load data from S3\n")
cat("   2. Explore data using dplyr and ggplot2\n")
cat("   3. Check docs/ for data dictionary and usage guide\n\n")

# Mark setup as complete
writeLines("", ".r_setup_complete")
cat("✓ Setup marker created (.r_setup_complete)\n\n")
