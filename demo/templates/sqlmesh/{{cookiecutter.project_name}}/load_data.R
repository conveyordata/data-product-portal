#!/usr/bin/env Rscript
#' Load Data from {{ cookiecutter.project_name }}
#'
#' This script demonstrates how to load data from S3 into R for analysis.
#' The data is stored as Parquet files organized by schema (staging, data_mart).
#'
#' Usage:
#'   source("load_data.R")
#'
#' Then access your data via:
#'   data_mart$your_table
#'   staging$your_table

cat("📊 Loading data from {{ cookiecutter.project_name }}\n")
cat("=================================================================\n\n")

# Load required libraries
suppressPackageStartupMessages({
  library(arrow)
  library(duckdb)
  library(dplyr)
})

# Load environment variables
if (file.exists(".env")) {
  for (line in readLines(".env")) {
    if (nchar(line) > 0 && !startsWith(line, "#") && grepl("=", line)) {
      parts <- strsplit(line, "=", fixed = TRUE)[[1]]
      if (length(parts) >= 2) {
        Sys.setenv(setNames(parts[2], parts[1]))
      }
    }
  }
}

# S3 configuration
endpoint_host <- Sys.getenv("S3_ENDPOINT_HOST", "rustfs")
access_key <- Sys.getenv("S3_ACCESS_KEY", "minioadmin")
secret_key <- Sys.getenv("S3_SECRET_KEY", "minioadmin")
bucket <- Sys.getenv("S3_BUCKET", "data-products")
prefix <- Sys.getenv("S3_PREFIX", "{{ cookiecutter.project_name }}")

cat("🔧 S3 Configuration:\n")
cat(sprintf("   Endpoint: %s:9000\n", endpoint_host))
cat(sprintf("   Location: s3://%s/%s/\n\n", bucket, prefix))

# Initialize DuckDB connection
con <- dbConnect(duckdb::duckdb())

# Load httpfs extension for S3 access
dbExecute(con, "INSTALL httpfs;")
dbExecute(con, "LOAD httpfs;")

# Configure S3 secret
s3_config <- sprintf("
  CREATE OR REPLACE SECRET s3_secret (
    TYPE S3,
    ENDPOINT '%s:9000',
    KEY_ID '%s',
    SECRET '%s',
    USE_SSL false,
    URL_STYLE 'path',
    REGION 'us-east-1'
  );
", endpoint_host, access_key, secret_key)

dbExecute(con, s3_config)

cat("📦 Loading data from S3...\n\n")

#' Load all Parquet files from a schema directory into a named list
#'
#' @param schema_name Name of the schema (e.g., "staging", "data_mart")
#' @return Named list of data frames
load_schema_data <- function(schema_name) {
  s3_path <- sprintf("s3://%s/%s/%s/*.parquet", bucket, prefix, schema_name)

  tryCatch({
    # Get list of files
    files_query <- sprintf("SELECT * FROM glob('%s')", s3_path)
    files <- dbGetQuery(con, files_query)

    if (nrow(files) == 0) {
      cat(sprintf("   %s/: No tables found\n", schema_name))
      return(list())
    }

    cat(sprintf("   %s/:\n", schema_name))

    # Load each file as a named element in the list
    schema_data <- list()
    for (file_path in files[[1]]) {
      table_name <- tools::file_path_sans_ext(basename(file_path))

      # Read parquet file into R data frame
      df <- dbGetQuery(con, sprintf("SELECT * FROM '%s'", file_path))
      schema_data[[table_name]] <- df

      cat(sprintf("      ✓ %s (%s rows)\n", table_name, format(nrow(df), big.mark = ",")))
    }

    return(schema_data)

  }, error = function(e) {
    cat(sprintf("   %s/: %s\n", schema_name, conditionMessage(e)))
    return(list())
  })
}

# Load data from different schemas
staging <- load_schema_data("staging")
data_mart <- load_schema_data("data_mart")

# Close DuckDB connection
dbDisconnect(con, shutdown = TRUE)

cat("\n✅ Data loaded successfully!\n\n")
cat("📊 Available datasets:\n")
if (length(staging) > 0) {
  cat(sprintf("   staging$%s\n", names(staging)))
}
if (length(data_mart) > 0) {
  cat(sprintf("   data_mart$%s\n", names(data_mart)))
}

cat("\n💡 Example usage:\n")
cat("   # View data\n")
cat("   View(data_mart$your_table)\n")
cat("   \n")
cat("   # Summary statistics\n")
cat("   summary(data_mart$your_table)\n")
cat("   \n")
cat("   # dplyr operations\n")
cat("   data_mart$your_table %>%\n")
cat("     filter(column > value) %>%\n")
cat("     group_by(category) %>%\n")
cat("     summarise(count = n())\n")
cat("\n")

# Clean up environment (keep only data objects)
rm(endpoint_host, access_key, secret_key, bucket, prefix, s3_config, con, load_schema_data)
