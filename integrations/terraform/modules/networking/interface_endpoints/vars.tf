variable "service" {}
variable "prefix" {}
variable "aws_region" {}
variable "vpc_id" {}
variable "allowed_cidr_ranges" {
  type = list(string)
}
variable "subnet_ids" {
  type = list(string)
}
