module "data_products" {
  source   = "../../modules/data_products"
  for_each = local.data_product_glossary

  prefix           = local.prefix
  account_name     = local.account_name
  conveyor_enabled = local.conveyor_enabled

  data_product_name   = each.key
  data_product_config = each.value

  environments = local.environments
  data_outputs = local.data_outputs
  datasets     = local.datasets
}
