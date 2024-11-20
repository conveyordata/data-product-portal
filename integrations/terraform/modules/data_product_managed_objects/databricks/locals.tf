locals {
  #  Handling paths for AWS resources
  bucket_glossary = var.environment_config.bucket_glossary
  # Default datalake bucket
  default_bucket = [for bucket_id, bucket in local.bucket_glossary : bucket if bucket.is_default][0]

  # Split outputs based on type
  dbx_outputs  = { for k, v in var.data_outputs : k => v.dbx[0] if length(v.dbx) > 0 }
  s3_outputs   = { for k, v in var.data_outputs : k => v.s3[0] if length(v.s3) > 0 }
  glue_outputs = { for k, v in var.data_outputs : k => v.glue[0] if length(v.glue) > 0 }
  # Distinguish between glue outputs on the database or table level
  glue_tables    = { for k, v in local.glue_outputs : k => v if v.table != "*" }
  glue_databases = { for k, v in local.glue_outputs : k => v if v.table == "*" }
}
