resource "databricks_group" "service_access_group" {
  provider = databricks.mws

  display_name = "${var.data_product_name}__${local.environment_name_map[var.environment]}__service_access_group"
}
// Link compute group to environment workspace
resource "databricks_mws_permission_assignment" "link_service_access_group" {
  provider = databricks.mws
  workspace_id = var.workspace_id
  principal_id = databricks_group.service_access_group.id
  permissions  = ["USER"]
}
