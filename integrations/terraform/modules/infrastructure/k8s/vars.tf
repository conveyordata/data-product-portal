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

variable "eks_admin_role_arns" {
  type    = list(string)
  default = []
}

variable "eks_version" {
  default = "1.28"
}

variable "cluster_name" {}

variable "cluster_endpoint_public_access" {
  type = bool
}

variable "cluster_endpoint_private_access" {
  type = bool
}
