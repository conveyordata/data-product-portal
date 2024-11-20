locals {
  external_locations = merge(
    {
      for output_id, s3 in local.s3_outputs :
      output_id => {
        name         = output_id
        url          = "s3://${local.bucket_glossary[s3.bucket_identifier].bucket_name}/${s3.suffix}/${s3.path}"
        data_product = var.data_outputs[output_id].owner
      }
    },
    {
      for output_id, database in local.glue_databases :
      output_id =>
      {
        name         = database.database_suffix
        url          = "s3://${local.bucket_glossary[database.bucket_identifier].bucket_name}/${database.database_path}"
        data_product = var.data_outputs[output_id].owner
      }
    },
    {
      for output_id, table in local.glue_tables :
      output_id =>
      {
        name         = "${table.database_suffix}__${table.table}"
        url          = "s3://${local.bucket_glossary[table.bucket_identifier].bucket_name}/${table.database_path}/${table.table_path}"
        data_product = var.data_outputs[output_id].owner
      }
    },
  )
}

// External locations
resource "databricks_external_location" "root_buckets" {
  for_each = local.bucket_glossary

  provider = databricks.workspace

  name            = "${each.key}__${var.environment}"
  url             = "s3://${each.value.bucket_name}"
  credential_name = var.environment_config.dbx_credential_name
}

// External volumes
resource "databricks_volume" "external_volumes" {
  for_each = local.external_locations

  provider = databricks.workspace

  name             = each.value.name
  catalog_name     = databricks_catalog.data_product_catalog[each.value.data_product].name
  schema_name      = databricks_schema.external_data_schema[each.value.data_product].name
  volume_type      = "EXTERNAL"
  storage_location = each.value.url
}
