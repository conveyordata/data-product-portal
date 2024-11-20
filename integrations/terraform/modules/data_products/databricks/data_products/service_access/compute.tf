resource "databricks_cluster" "default_cluster" {
  provider = databricks.workspace

  cluster_name            = "Cluster ${var.data_product_name}__${local.environment_name_map[var.environment]}"
  spark_version           = local.merged_cluster_params.spark_version
  node_type_id            = local.merged_cluster_params.node_type_id
  data_security_mode      = local.merged_cluster_params.data_security_mode
  num_workers             = local.merged_cluster_params.num_workers
  autotermination_minutes = local.merged_cluster_params.autotermination_minutes
  # Optional attributes
  custom_tags      = lookup(local.merged_cluster_params, "custom_tags", null)
  single_user_name = lookup(local.merged_cluster_params, "single_user_name", null)
  no_wait = true
}

// Permissions
resource "databricks_permissions" "cluster" {
  provider = databricks.workspace
  cluster_id = databricks_cluster.default_cluster.id
  access_control {
    group_name       = databricks_group.service_access_group.display_name
    permission_level = "CAN_RESTART"
  }
}
