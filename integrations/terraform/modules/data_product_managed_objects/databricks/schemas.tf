// Databricks-native data output schemas & tables
resource "databricks_schema" "public_schemas" {
  for_each     = local.dbx_outputs
  provider     = databricks.workspace
  catalog_name = databricks_catalog.data_product_catalog[var.data_outputs[each.key].owner].name
  name         = "${each.value.schema_identifier}"
  storage_root = "s3://${local.bucket_glossary[each.value.bucket_identifier].bucket_name}/${each.value.schema_path}"
}

// Private schemas per Data Product
resource "databricks_schema" "private_schemas" {
  for_each     = local.private_schemas
  provider     = databricks.workspace
  catalog_name = databricks_catalog.data_product_catalog[each.key].name
  name         = each.value
  storage_root = "s3://${local.default_bucket}/${each.key}/private"
}

// External data schema
resource "databricks_schema" "external_data_schema" {
  for_each = local.external_schemas
  provider     = databricks.workspace
  catalog_name = databricks_catalog.data_product_catalog[each.key].name
  name         = each.value
  # storage_root = // TODO: set this up (maybe input from environment?)
}
