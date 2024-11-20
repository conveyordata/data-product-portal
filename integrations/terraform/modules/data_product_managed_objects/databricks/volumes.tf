locals {
  external_locations = merge(
    {
      for bucket_name, bucket in local.s3_outputs :
      bucket_name => {
        name         = bucket_name
        url          = "s3://${local.bucket_glossary[bucket.bucket_identifier].bucket_name}/${bucket.suffix}/${bucket.path}"
        data_product = var.data_outputs[bucket_name].owner
      }
    },
    {
      for database_name, database in local.glue_databases :
      database_name =>
      {
        name         = database.database_suffix
        url          = "s3://${local.bucket_glossary[database.bucket_identifier].bucket_name}/${database.database_path}"
        data_product = var.data_outputs[database_name].owner
      }
    },
    {
      for table_name, table in local.glue_tables :
      table_name =>
      {
        name         = "${table.database_suffix}__${table.table}"
        url          = "s3://${local.bucket_glossary[table.bucket_identifier].bucket_name}/${table.database_path}/${table.table_path}"
        data_product = var.data_outputs[table_name].owner
      }
    },
  )
}

// External locations
resource "databricks_external_location" "root_buckets" {
  for_each        = { for bucket_id, bucket in local.bucket_glossary : bucket_id => bucket.bucket_name }
  provider        = databricks.workspace
  name            = "${each.key}__${local.environment_name_map[var.environment]}"
  url             = "s3://${each.value}"
  credential_name = var.environment_config.dbx_credential_name
  force_destroy   = true
}

// External volumes
resource "databricks_volume" "external_volumes" {
  for_each = local.external_locations

  provider         = databricks.workspace
  name             = each.value.name
  catalog_name     = databricks_catalog.data_product_catalog[each.value.data_product].name
  schema_name      = databricks_schema.external_data_schema[each.value.data_product].name
  volume_type      = "EXTERNAL"
  storage_location = each.value.url
}
