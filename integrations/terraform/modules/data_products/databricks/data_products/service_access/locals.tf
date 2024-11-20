locals {
  environment_name_map = {
    "development" = "dev",
    "production"  = "prd"
  }
  default_cluster_params = {
    spark_version           = "15.4.x-scala2.12"
    node_type_id            = "m5d.large"
    data_security_mode      = "USER_ISOLATION"
    num_workers             = 1
    autotermination_minutes = 20
  }
  // Filter out null values from the environment config from optional vars (There has to be a better way of doing this)
  env_cluster_params = {
    for k, v in var.environment_config.dbx_env_cluster_params : k => v
    if v != null
  }
  merged_cluster_params = merge(local.default_cluster_params, local.env_cluster_params)
}
