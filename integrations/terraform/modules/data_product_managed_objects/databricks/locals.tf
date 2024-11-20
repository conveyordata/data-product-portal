locals {
  #  Handling paths for AWS resources
  bucket_glossary = var.environment_config.bucket_glossary

  # Default datalake bucket
  default_bucket = [for bucket_id, bucket in local.bucket_glossary : bucket.bucket_name if bucket.is_default][0]
  environment_name_map = {
    "development" = "dev",
    "production"  = "prd"
  }
  # Select outputs for the current business unit
  dbx_outputs    = { for k, v in var.data_outputs : k => v.dbx[0] if length(v.dbx) > 0 }
  dbx_tables     = { for k, v in local.dbx_outputs : k => v if v.table != "*"}
  s3_outputs     = { for k, v in var.data_outputs : k => v.s3[0] if length(v.s3) > 0 }
  glue_outputs   = { for k, v in var.data_outputs : k => v.glue[0] if length(v.glue) > 0 }
  glue_tables    = { for k, v in local.glue_outputs : k => v if v.table != "*"}
  glue_databases = { for k, v in local.glue_outputs : k => v if v.table == "*"}
  # data_products_with_external_outputs = distinct([for k, v in var.data_outputs : v.owner if !contains(keys(local.dbx_outputs), k)])
  # TODO: Consider both external inputs and outputs
  data_products_with_external_connections = [for k, v in var.data_product_glossary : k]

  #  Create maps between public and private schemas
  public_schemas  = { for dbx_output_id, meta in local.dbx_outputs : dbx_output_id => meta.schema_identifier }
  public_tables   = { for dbx_output_id, meta in local.dbx_tables : dbx_output_id => meta.table }
  private_schemas = { for data_product_id, _ in var.data_product_glossary : data_product_id => "private" }
  external_schemas = { for data_product_id in local.data_products_with_external_connections : data_product_id => "external" }
}
