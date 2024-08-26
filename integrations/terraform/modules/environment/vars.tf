variable "prefix" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "aws_account_id" {
  type = string
}

variable "account_name" {
  type = string
}

variable "env" {
  type = string
}

variable "conveyor_enabled" {
  type = bool
}

variable "can_read_from" {
  type = list(string)
}

variable "conveyor_oidc_provider_url" {}

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

variable "datalake_vpc_restricted" {
  type = bool
}

variable "athena_enabled" {
  type    = bool
  default = true
}

variable "redshift_spectrum_enabled" {
  type    = bool
  default = false
}

variable "ingress" {
  type = bool
}

variable "egress" {
  type = bool
}

variable "versioning_duration" {
  default = 30
}

variable "s3_access_logs_prefix" {
  default = "s3-access-logs"
}

variable "database_glossary" {
  type = map(object({
    s3 = string
  }))
}
