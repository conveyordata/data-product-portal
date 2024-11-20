module "users" {
  source = "./single_user"
  for_each = toset(var.data_product_config.users)

  user = each.value
  access_groups = local.all_access_groups
  data_product_name = var.data_product_name
  environment = var.environment
  prefix = var.prefix

  providers = {
    databricks.mws       = databricks.mws
    databricks.workspace = databricks.workspace
  }
}
