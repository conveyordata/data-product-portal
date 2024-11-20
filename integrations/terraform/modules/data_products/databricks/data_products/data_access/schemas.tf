locals {
  write_dbx_outputs = [for output_id, data_output in var.data_outputs : output_id if data_output.owner == var.data_product_name && contains(local.dbx_outputs, output_id) && !contains(local.dbx_tables, output_id)]
  read_dbx_outputs = concat(
    [for output_id in local.read_datasets_items : output_id if contains(local.dbx_outputs, output_id)],
    [for output_id, data_output in var.data_outputs : output_id if data_output.owner == var.data_product_name && contains(local.dbx_tables, output_id)]
  )

  write_schemas = distinct(concat(
    [for output_id in local.write_dbx_outputs : var.managed_objects.public_schemas[output_id]],
    [var.managed_objects.private_schemas[var.data_product_name]]
  ))
  read_schemas = distinct(concat(
    [for output_id in local.read_dbx_outputs : var.managed_objects.public_schemas[output_id]],
    local.write_schemas
  ))
  # TODO: We are filtering the external schemas using all read outputs, but we should only consider the external ones
  external_schemas_list = distinct(concat(
    [for data_output in local.read_datasets_items_external : var.data_outputs[data_output].owner],
    [var.data_product_name]
  ))
  external_schemas = {
    for data_product in local.external_schemas_list :
    data_product => var.managed_objects.external_data_schemas[data_product]
  }
}
resource "databricks_grant" "external_data_schema_access" {
  provider = databricks.workspace
  for_each = local.external_schemas

  schema     = each.value
  principal  = databricks_group.read_access_group.display_name
  privileges = local.external_schema_read_permissions
}

resource "databricks_grant" "schema_read_access" {
  provider = databricks.workspace
  for_each = toset(local.read_schemas)

  schema     = each.value
  principal  = databricks_group.read_access_group.display_name
  privileges = local.schema_read_permissions
}

resource "databricks_grant" "schema_write_access" {
  provider = databricks.workspace
  for_each = toset(local.write_schemas)

  schema     = each.value
  principal  = databricks_group.write_access_group.display_name
  privileges = local.schema_write_permissions
}
