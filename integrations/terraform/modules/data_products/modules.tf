module "data_access" {
  source   = "./data_access"
  for_each = var.environments

  prefix         = var.prefix
  aws_region     = var.aws_region
  aws_account_id = var.aws_account_id
  account_name   = var.account_name

  environment        = each.key
  environment_config = each.value
  data_product_name       = var.data_product_name
  data_product_config     = var.data_product_config
  data_outputs           = var.data_outputs
  datasets        = var.datasets
}

module "roles" {
  source   = "./roles"
  for_each = var.environments

  prefix         = var.prefix
  aws_region     = var.aws_region
  aws_account_id = var.aws_account_id
  account_name   = var.account_name

  data_product_name   = var.data_product_name
  data_product_config = var.data_product_config

  environment        = each.key
  environment_config = each.value

  read_data_access_policy_arns = concat(
    module.data_access[each.key].read_policy_arns,
    flatten([for env in var.environments[each.key].can_read_from : module.data_access[env].read_policy_arns])
  )
  write_data_access_policy_arns = module.data_access[each.key].write_policy_arns
}

module "users" {
  source   = "./users"
  for_each = var.data_product_config.services.create_iam_user ? var.environments : {}

  prefix         = var.prefix
  aws_region     = var.aws_region
  aws_account_id = var.aws_account_id
  account_name   = var.account_name

  data_product_name   = var.data_product_name
  data_product_config = var.data_product_config

  environment        = each.key
  environment_config = each.value

  service_policy_arns = module.roles[each.key].service_policy_arns
  read_data_access_policy_arns = concat(
    module.data_access[each.key].read_policy_arns,
    flatten([for env in var.environments[each.key].can_read_from : module.data_access[env].read_policy_arns])
  )
  write_data_access_policy_arns = module.data_access[each.key].write_policy_arns
}
