locals {
  environment_name_map = {
    "development" = "dev",
    "production"  = "prd"
  }
  dbx_outputs_map     = { for k, v in var.data_outputs : k => v.dbx[0] if length(v.dbx) > 0 }
  dbx_outputs         = [for output_id, _ in local.dbx_outputs_map : output_id]
  dbx_tables          = [for output_id, output_meta in local.dbx_outputs_map : output_id if output_meta.table != "*"]
  read_datasets_items = flatten([for dataset in var.data_product_config.read_datasets : var.datasets[dataset].data_outputs])
  read_datasets_items_external = [for data_output in local.read_datasets_items : data_output if length(var.data_outputs[data_output].dbx) == 0]
  // R/W permissions - Schemas
  external_schema_read_permissions = ["USE_SCHEMA", "EXECUTE"]
  schema_read_permissions          = ["SELECT", "USE_SCHEMA", "EXECUTE"]
  schema_write_permissions         = ["MODIFY", "APPLY_TAG", "READ_VOLUME", "WRITE_VOLUME", "CREATE_TABLE", "CREATE_FUNCTION", "CREATE_VOLUME"]
  // R/W permissions - Tables
  table_read_permissions  = ["SELECT"]
  table_write_permissions = ["MODIFY", "APPLY_TAG"]
  // R/W permissions - Volumes
  volume_read_permissions  = ["READ_VOLUME"]
  volume_write_permissions = ["WRITE_VOLUME", "APPLY_TAG"]
}
