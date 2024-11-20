module "data_product_managed_objects" {
  source   = "../../../modules/data_product_managed_objects/aws"
  for_each = local.environments

  prefix = local.prefix

  environment        = each.key
  environment_config = each.value

  data_outputs = local.data_outputs
}

module "data_products" {
  source   = "../../../modules/data_products/aws"
  for_each = local.data_product_glossary

  prefix           = local.prefix
  account_name     = local.account_name
  conveyor_enabled = local.conveyor_enabled

  data_product_name   = each.key
  data_product_config = each.value

  environments = local.environments
  data_outputs = local.data_outputs
  datasets     = local.datasets

  managed_objects = module.data_product_managed_objects
}
