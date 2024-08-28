variable "prefix" {}
variable "aws_region" {}
variable "aws_account_id" {}
variable "account_name" {}
variable "vpc_name" {}
variable "vpc_cidr" {}
variable "vpc_secondary_cidr" {}
variable "routable_subnets" {
  type = map(object({
    az   = string
    cidr = string
  }))
}
variable "non_routable_subnets" {
  type = map(object({
    az   = string
    cidr = string
  }))
}
variable "create_vpc_endpoints" {
  type = bool
}
variable "enforce_endpoint_restrictions" {
  type = bool
}
