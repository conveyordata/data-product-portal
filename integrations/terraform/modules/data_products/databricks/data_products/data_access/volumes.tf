locals {
  // External volumes
  write_outputs = distinct([
    for output_id, data_output in var.data_outputs :
    output_id if data_output.owner == var.data_product_name
  ])
  read_outputs = distinct(local.read_datasets_items)

  write_volumes = flatten([
    for output_id, locations in var.managed_objects.external_volumes :
    locations if anytrue([for write_output in local.write_outputs : can(regex(write_output, output_id))])
  ])

  # TODO: Should theoretically be distinct, but this breaks terraform apply
  read_volumes = flatten([
    for output_id, locations in var.managed_objects.external_volumes :
    locations if anytrue([for read_output in concat(local.read_outputs, local.write_outputs) : can(regex(read_output, output_id))])
  ])
}
resource "databricks_grant" "read_volume" {
  provider = databricks.workspace

  for_each   = { for idx, volume in local.read_volumes : idx => volume }
  volume     = each.value
  principal  = databricks_group.read_access_group.display_name
  privileges = local.volume_read_permissions
}

resource "databricks_grant" "write_volume" {
  provider = databricks.workspace

  for_each   = { for idx, volume in local.write_volumes : idx => volume }
  volume     = each.value
  principal  = databricks_group.write_access_group.display_name
  privileges = local.volume_write_permissions
}
