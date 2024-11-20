module "data_products" {
  source   = "./data_products"
  for_each = local.current_purpose_data_products

  prefix = var.prefix

  data_product_name   = each.key
  data_product_config = each.value
  data_product_glossary = var.data_product_glossary
  managed_objects = var.managed_objects
  environment = var.environment

  environment_config = var.environment_config

  data_outputs    = var.data_outputs
  datasets        = var.datasets
  workspace_id    = var.workspace_id
  workspaces_config = var.workspaces_config
  business_unit     = var.business_unit
  providers = {
    databricks.mws       = databricks.mws
    databricks.root_workspace = databricks.root_workspace
    databricks.workspace = databricks.workspace
  }
}
