locals {
  environment_name_map = {
    "development" = "dev",
    "production"  = "prd"
  }
  account_id = var.environment_config.dbx_account_id
  service_access_group_principal_id = var.service_access_groups.service_access_group_acl_principal_id
  read_access_groups = [
      for environment in concat(var.environment_config.can_read_from, [var.environment]) :
      var.data_access_groups.read_access_group
  ]

  all_access_groups = concat(
      local.read_access_groups,
      [var.data_access_groups.write_access_group],
      [var.service_access_groups.service_access_group],
  )
}
