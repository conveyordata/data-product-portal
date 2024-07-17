variable "account_name" {}
variable "aws_account_id" {}
variable "aws_region" {}
variable "prefix" {}

variable "alb_ingress_version" {
  default = "1.4.8"
}

variable "account_config" {
  type = object({
    certificate_arn = string
    hosted_zone     = string
    hosted_zone_arn = string
    hostname        = string
  })
}

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

variable "k8s_config" {
  type = object({
    cluster_name           = string
    cluster_endpoint       = string
    oidc_provider_arn      = string
    cluster_node_role_arn  = string
    node_security_group_id = string
  })
}
