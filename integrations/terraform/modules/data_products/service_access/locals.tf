locals {
  # ? Add validation?
  # Default datalake bucket
  default_bucket = [for bucket_id, bucket in var.environment_config.bucket_glossary : bucket if bucket.is_default][0]
}
