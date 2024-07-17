module "k8s" {
  count = local.create_k8s_cluster ? 1 : 0

  source = "./k8s"

  prefix         = var.prefix
  aws_region     = var.aws_region
  aws_account_id = var.aws_account_id
  account_name   = var.account_name

  vpc_config                      = var.vpc_config
  cluster_name                    = var.infrastructure_config.cluster_name
  eks_admin_role_arns             = var.infrastructure_config.eks_admin_role_arns
  cluster_endpoint_public_access  = var.infrastructure_config.cluster_endpoint_public_access
  cluster_endpoint_private_access = var.infrastructure_config.cluster_endpoint_private_access
}

module "k8s_infrastructure" {
  count  = local.create_k8s_cluster ? 1 : 0
  source = "./k8s_infrastructure"

  prefix         = var.prefix
  aws_region     = var.aws_region
  aws_account_id = var.aws_account_id
  account_name   = var.account_name

  k8s_config     = module.k8s[0]
  vpc_config     = var.vpc_config
  account_config = var.account_config
}

module "datahub" {
  count  = local.create_k8s_cluster ? 1 : 0
  source = "./datahub"

  prefix         = var.prefix
  aws_region     = var.aws_region
  aws_account_id = var.aws_account_id
  account_name   = var.account_name

  #k8s_infra_config = module.k8s_infrastructure[0] # no output defined yet
  vpc_config     = var.vpc_config
  k8s_config     = module.k8s[0]
  account_config = var.account_config
}
