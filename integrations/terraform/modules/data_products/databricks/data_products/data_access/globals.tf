# # TODO: Here we implement the can_read_from (however disabled for demo purposes)
# resource "databricks_mws_permission_assignment" "workspace_access" {
#   provider     = databricks.mws
#   workspace_id = var.workspace_id
#   principal_id = databricks_group.read_access_group.id
#   permissions  = ["USER"]
# }
