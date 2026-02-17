#' RStudio Configuration for {{ cookiecutter.project_name }}
#'
#' This file is automatically loaded when RStudio opens this project.
#' It sets up the environment for working with this data product.

# Welcome message
cat("\n")
cat("╔════════════════════════════════════════════════════════════════╗\n")
cat("║                                                                ║\n")
cat("║  Welcome to {{ cookiecutter.project_name }}                   ║\n")
cat("║  Data Product Portal - Ready for Analysis                     ║\n")
cat("║                                                                ║\n")
cat("╚════════════════════════════════════════════════════════════════╝\n")
cat("\n")

# Check if setup has been run
if (!file.exists(".r_setup_complete")) {
  cat("📦 First time setup required\n")
  cat("   Run: source('setup.R')\n")
  cat("   This will install required packages and configure S3 access.\n\n")
} else {
  cat("✅ Environment is ready!\n\n")
  cat("📚 Quick start:\n")
  cat("   • Load data:     source('load_data.R')\n")
  cat("   • View docs:     browseURL('docs/index.html')\n")
  cat("   • Test S3:       source('test_s3_access.py')  # Run in terminal\n")
  cat("\n")
  cat("📊 Available scripts:\n")
  cat("   • setup.R         - Install packages and configure environment\n")
  cat("   • load_data.R     - Load data from S3 into R\n")
  cat("   • export_to_s3.py - Export SQLMesh data to S3 (Python)\n")
  cat("\n")
  cat("🗂️  Project structure:\n")
  cat("   • models/         - SQLMesh transformation models\n")
  cat("   • docs/           - Quarto documentation\n")
  cat("   • .env            - S3 credentials (DO NOT COMMIT)\n")
  cat("\n")
}

cat("💡 Tip: Press Ctrl+Shift+F10 to restart R session\n")
cat("\n")

# Set options for better R experience
options(
  repos = c(CRAN = "https://cloud.r-project.org/"),
  stringsAsFactors = FALSE,
  max.print = 1000,
  scipen = 999  # Avoid scientific notation
)

# Auto-load commonly used libraries if available
.auto_load_libs <- function() {
  libs <- c("dplyr", "ggplot2")
  for (lib in libs) {
    if (requireNamespace(lib, quietly = TRUE)) {
      suppressPackageStartupMessages(library(lib, character.only = TRUE))
    }
  }
}

# Uncomment to auto-load libraries on startup
# .auto_load_libs()

# Helper function to quickly load data
load_data_quick <- function() {
  cat("Loading data from S3...\n")
  source("load_data.R")
}
