terraform {
  required_version = "1.9.2"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    conveyor = {
      source = "datamindedbe/conveyor"
    }
  }
}

provider "aws" {
  region              = local.aws_region
  allowed_account_ids = [local.aws_account_id]
  default_tags {
    tags = local.mandatory_tags
  }
}

# TODO: enable when you set up a kubernetes cluster for datahub and portal or interact directly with conveyor
# provider "conveyor" {}
#
# data "aws_eks_cluster" "cluster" {
#   name = local.infrastructure.cluster_name
# }
#
# data "aws_eks_cluster_auth" "cluster" {
#   name = local.infrastructure.cluster_name
# }
#
# provider "kubernetes" {
#   host                   = data.aws_eks_cluster.cluster.endpoint
#   cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority.0.data)
#   token                  = data.aws_eks_cluster_auth.cluster.token
# }
#
# provider "helm" {
#   kubernetes {
#     host                   = data.aws_eks_cluster.cluster.endpoint
#     cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority.0.data)
#     token                  = data.aws_eks_cluster_auth.cluster.token
#   }
# }
