output "write_access_group" {
  value = databricks_group.write_access_group.id
}
output "read_access_group" {
  value = databricks_group.read_access_group.id
}

output "external_schemas" {
  value = local.external_schemas
}
output "read_datasets_items" {
  value = local.read_datasets_items
}
output "read_datasets_items_external" {
  value = local.read_datasets_items_external
}
