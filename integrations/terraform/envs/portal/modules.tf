# module "account" {
#   source = "../../modules/account"
#
#   aws_region      = local.aws_region
#   hosted_zone     = local.account.hosted_zone
#   hosted_zone_arn = local.account.hosted_zone_arn
#   hostname        = local.account.hostname
# }

module "networking" {
  source = "../../modules/networking"

  aws_region     = local.aws_region
  prefix         = local.prefix
  account_name   = local.account_name
  aws_account_id = local.aws_account_id

  # TODO: cleanup to be a bit more consistent and provide config as a whole
  vpc_name             = local.networking.vpc_name
  vpc_cidr             = local.networking.vpc_cidr
  vpc_secondary_cidr   = local.networking.vpc_secondary_cidr
  routable_subnets     = local.networking.routable_subnets
  non_routable_subnets = local.networking.non_routable_subnets

  create_vpc_endpoints          = false
  enforce_endpoint_restrictions = false
}

module "infrastructure" {
  source = "../../modules/infrastructure"

  aws_region     = local.aws_region
  prefix         = local.prefix
  account_name   = local.account_name
  aws_account_id = local.aws_account_id

  account_config        = local.account
  vpc_config            = module.networking
  infrastructure_config = local.infrastructure
}

module "environments" {
  source   = "../../modules/environment"
  for_each = local.environments

  aws_region       = local.aws_region
  prefix           = local.prefix
  account_name     = local.account_name
  aws_account_id   = local.aws_account_id
  conveyor_enabled = local.conveyor_enabled

  env = each.key
  # TODO: pass config as a whole
  vpc_config                 = each.value["vpc_config"]
  datalake_vpc_restricted    = each.value["datalake_vpc_restricted"]
  ingress                    = each.value["ingress"]
  egress                     = each.value["egress"]
  can_read_from              = each.value["can_read_from"]
  conveyor_oidc_provider_url = each.value["conveyor_oidc_provider_url"]

  database_glossary = local.database_glossary
}

module "data_products" {
  source   = "../../modules/data_products"
  for_each = local.data_product_glossary

  aws_region       = local.aws_region
  prefix           = local.prefix
  account_name     = local.account_name
  aws_account_id   = local.aws_account_id
  conveyor_enabled = local.conveyor_enabled

  data_product_name   = each.key
  data_product_config = each.value

  environments = module.environments
  data_outputs     = local.data_outputs
  datasets  = local.datasets
}
