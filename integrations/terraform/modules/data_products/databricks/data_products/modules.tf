module "data_access" {
  source   = "./data_access"

  prefix              = var.prefix
  data_product_name   = var.data_product_name
  data_product_config = var.data_product_config

  environment        = var.environment
  environment_config = var.environment_config
  workspace_id = var.workspace_id

  data_outputs = var.data_outputs
  datasets     = var.datasets
  managed_objects = var.managed_objects

  providers = {
    databricks.mws       = databricks.mws
    databricks.workspace = databricks.root_workspace # We link data access groups to the root workspace
  }
}

module "service_access" {
  source = "./service_access"

  prefix              = var.prefix
  data_product_name   = var.data_product_name
  data_product_config = var.data_product_config

  environment        = var.environment
  environment_config = var.environment_config

  workspace_id = var.workspace_id

  providers = {
    databricks.mws       = databricks.mws
    databricks.workspace = databricks.workspace
  }
}

module "users" {
  source = "./users"

  prefix              = var.prefix
  data_product_name   = var.data_product_name
  data_product_config = var.data_product_config

  environment        = var.environment
  environment_config = var.environment_config

  data_access_groups = module.data_access
  service_access_groups = module.service_access

  providers = {
    databricks.mws       = databricks.mws
    databricks.workspace = databricks.workspace
  }
}

module "service_principal" {
  source = "./service_principal"

  prefix              = var.prefix
  data_product_name   = var.data_product_name
  data_product_config = var.data_product_config

  environment        = var.environment
  environment_config = var.environment_config

  data_access_groups = module.data_access
  service_access_groups = module.service_access

  providers = {
    databricks.mws       = databricks.mws
    databricks.workspace = databricks.workspace
  }
}

module "catalog_binding" {
  source = "./catalog_binding"

  prefix              = var.prefix
  data_product_name   = var.data_product_name
  data_product_config = var.data_product_config

  environment        = var.environment
  data_outputs      = var.data_outputs
  datasets          = var.datasets
  data_product_glossary = var.data_product_glossary
  business_unit     = var.business_unit
  workspaces_config = var.workspaces_config
  managed_objects = var.managed_objects
  providers = {
    databricks.mws       = databricks.mws
    databricks.workspace = databricks.root_workspace
  }
}
