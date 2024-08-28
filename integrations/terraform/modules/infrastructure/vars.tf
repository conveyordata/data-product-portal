variable "prefix" {}
variable "aws_region" {}
variable "aws_account_id" {}
variable "account_name" {}

variable "vpc_config" {
  type = object({
    vpc_id                   = string
    vpc_cidr_block           = string
    vpc_secondary_cidr_block = string
    s3_endpoint_id           = string
    route_table_ids          = list(string)
    routable_subnets = map(object({
      subnet_id         = string
      subnet_cidr_block = string
      az                = string
    }))
    non_routable_subnets = map(object({
      subnet_id         = string
      subnet_cidr_block = string
      az                = string
    }))
  })
}

variable "account_config" {
  type = object({
    certificate_arn = string
    hosted_zone     = string
    hosted_zone_arn = string
    hostname        = string
  })
}

variable "infrastructure_config" {
  type = object({
    create_jump_host                = bool
    create_datahub                  = bool
    cluster_name                    = string
    eks_admin_role_arns             = list(string)
    cluster_endpoint_public_access  = bool
    cluster_endpoint_private_access = bool
  })
}
