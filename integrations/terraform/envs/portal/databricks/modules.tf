# Create UC resources in the root workspace
module "create_uc_resources" {
  source   = "../../../modules/data_product_managed_objects/databricks"
  for_each = local.environments
  prefix = local.prefix

  data_product_glossary = local.data_product_glossary
  data_outputs          = local.data_outputs
  datasets              = local.datasets

  environment        = each.key
  environment_config = each.value

  providers = {
    databricks.mws       = databricks.mws
    databricks.workspace = databricks.root-workspace
  }
}

# Setup workspaces for each purpose
module "workspace_setup_business_unit_1_dev" {
  source = "../../../modules/data_products/databricks"
  prefix = local.prefix

  data_outputs          = local.data_outputs
  datasets              = local.datasets
  data_product_glossary = local.data_product_glossary
  managed_objects     = module.create_uc_resources[local.workspaces_config["business-unit-1-dev"]["environment"]]
  environment        = local.workspaces_config["business-unit-1-dev"]["environment"]
  environment_config = local.environments[local.workspaces_config["business-unit-1-dev"]["environment"]]
  business_unit      = "business-unit-1"
  workspace_id       = local.workspaces_config["business-unit-1-dev"]["id"]
  workspaces_config  = local.workspaces_config
  providers = {
    databricks.mws       = databricks.mws
    databricks.root_workspace = databricks.root-workspace
    databricks.workspace = databricks.workspace-business-unit-1-dev
  }
}

module "workspace_setup_business_unit_1_prd" {
  source = "../../../modules/data_products/databricks"
  prefix = local.prefix

  data_outputs          = local.data_outputs
  datasets              = local.datasets
  data_product_glossary = local.data_product_glossary
  managed_objects     = module.create_uc_resources[local.workspaces_config["business-unit-1-prd"]["environment"]]
  environment        = local.workspaces_config["business-unit-1-prd"]["environment"]
  environment_config = local.environments[local.workspaces_config["business-unit-1-prd"]["environment"]]
  business_unit      = "business-unit-1"
  workspace_id       = local.workspaces_config["business-unit-1-prd"]["id"]
  workspaces_config  = local.workspaces_config

  providers = {
    databricks.mws       = databricks.mws
    databricks.root_workspace = databricks.root-workspace
    databricks.workspace = databricks.workspace-business-unit-1-prd
  }
}

module "workspace_setup_business_unit_2_dev" {
  source = "../../../modules/data_products/databricks"
  prefix = local.prefix

  data_outputs          = local.data_outputs
  datasets              = local.datasets
  data_product_glossary = local.data_product_glossary
  managed_objects     = module.create_uc_resources[local.workspaces_config["business-unit-2-dev"]["environment"]]
  environment        = local.workspaces_config["business-unit-2-dev"]["environment"]
  environment_config = local.environments[local.workspaces_config["business-unit-2-dev"]["environment"]]
  business_unit      = "business-unit-2"
  workspace_id       = local.workspaces_config["business-unit-2-dev"]["id"]
  workspaces_config  = local.workspaces_config
  providers = {
    databricks.mws       = databricks.mws
    databricks.root_workspace = databricks.root-workspace
    databricks.workspace = databricks.workspace-business-unit-2-dev
  }
}

module "workspace_setup_business_unit_2_prd" {
  source = "../../../modules/data_products/databricks"
  prefix = local.prefix

  data_outputs          = local.data_outputs
  datasets              = local.datasets
  data_product_glossary = local.data_product_glossary
  managed_objects     = module.create_uc_resources[local.workspaces_config["business-unit-2-prd"]["environment"]]
  environment        = local.workspaces_config["business-unit-2-prd"]["environment"]
  environment_config = local.environments[local.workspaces_config["business-unit-2-prd"]["environment"]]
  business_unit      = "business-unit-2"
  workspace_id       = local.workspaces_config["business-unit-2-prd"]["id"]
  workspaces_config  = local.workspaces_config
  providers = {
    databricks.mws       = databricks.mws
    databricks.root_workspace = databricks.root-workspace
    databricks.workspace = databricks.workspace-business-unit-2-prd
  }
}
