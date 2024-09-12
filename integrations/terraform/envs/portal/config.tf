locals {
  # This prefix will be used for all of your created resources
  prefix = "portal"
  # The AWS account ID you want to add your AWS resources to
  aws_account_id = "123456789012"
  # Name of the AWS account
  account_name = "data-platform"
  # Region where you want to deploy resources to
  aws_region = "eu-west-1"

  # Choose whether you want to set up Conveyor integrations
  conveyor_enabled = false

  # Tags that will be set for all AWS services
  tags = {
    Environment = local.account_name
    Project     = local.prefix
  }

#   # Choose whether you want to create a jump host
#   create_jump_host = true
#   # Choose whether you want to set-up a datahub data catalog on a EKS cluster for your data platform
#   create_datahub = false

#   # Account level configuration. This information is only relevant if you enable services running on the EKS cluster
#   account = {
#     # The public hosted zone arn you want to use for exposing data platform services to. Leave empty if NA
#     hosted_zone_arn = "arn:aws:route53:::hostedzone/xxxxxxxxxxxxxxxxxxx"
#     # The public hosted zone you want to use for exposing data platform services to. Leave empty if NA
#     hosted_zone = "acme.com"
#     # The hostname you want to use for exposing data platform services to. Leave empty if NA
#     hostname = "data-platform"
#     # certificate_arn of linked to the hosted zone
#     certificate_arn = ""
#   }

#   # networking configuration that will set-up a VPC structure with secondary CIDR with nat gateway between routable
#   # and non-routable subnets
#   networking = {
#     # Name of the VPC to be created
#     vpc_name = "${local.prefix}-vpc-${local.account_name}"
#     # CIDR range of the VPC (cidr of routable subnets)
#     vpc_cidr = "10.0.0.0/24"
#     # CIDR range of non-routable part (cidr of non-routable subnets)
#     vpc_secondary_cidr = "100.64.0.0/16"
#     # Subnet configuration of routable subnets
#     routable_subnets = {
#       a = {
#         az   = "${local.aws_region}a"
#         cidr = "10.0.0.0/26"
#       }
#       b = {
#         az   = "${local.aws_region}b"
#         cidr = "10.0.0.64/26"
#       }
#       c = {
#         az   = "${local.aws_region}c"
#         cidr = "10.0.0.128/25"
#       }
#     }
#     # Subnet configuration of non-routable subnets
#     non_routable_subnets = {
#       a = {
#         az   = "${local.aws_region}a"
#         cidr = "100.64.0.0/17"
#       }
#       b = {
#         az   = "${local.aws_region}b"
#         cidr = "100.64.128.0/18"
#       }
#       c = {
#         az   = "${local.aws_region}c"
#         cidr = "100.64.192.0/18"
#       }
#     }
#     # Defines whether VPC endpoints need to be created for specific AWS services
#     create_vpc_endpoints = false
#     # Check whether endpoint network restrictions should be enforced for resources like S3
#     enforce_endpoint_restrictions = false
#   }
#
#   # Infrastructure related configuration
#   infrastructure = {
#     # Infrastructure config flags
#     create_jump_host = local.create_jump_host
#     create_datahub   = local.create_datahub
#     # EKS cluster name where additional services will be installed in. i.e. datahub
#     cluster_name = "${local.prefix}-${local.aws_eks}-kubernetes-${local.account_name}"
#     # Define additional roles that can administer the EKS cluster
#     eks_admin_role_arns = []
#     # Define whether cluster is publicly available
#     cluster_endpoint_public_access = true
#     # Define whether cluster endpoints are privately available inside the VPC
#     cluster_endpoint_private_access = false
#   }

#   # Configuration of data environments in the data platform setup
#   environments = {
#     # dev data environment
#     dev = {
#       # VPC network where data environment should be bound to
#       vpc_config = module.networking
#       # Enforce that data only can be accessed via that network
#       datalake_vpc_restricted = false
#       # Creation of ingress buckets for x-account data transfer
#       ingress = true
#       # Creation of egress buckets for x-account data transfer
#       egress = true
#       # Allow dev data environment roles to read from prd data environment
#       can_read_from = ["prd"]
#       # OIDC provider URL of the Conveyor EKS cluster. Leave empty if not
#       conveyor_oidc_provider_url = ""
#     }
#     # prd data environment
#     prd = {
#       vpc_config              = module.networking
#       datalake_vpc_restricted = false
#       ingress                 = true
#       egress                  = true
#       # prd data environment can only read from prd data environment
#       can_read_from              = []
#       conveyor_oidc_provider_url = ""
#     }
#   }
}
