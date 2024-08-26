variable "aws_region" {
  type = string
}

variable "hosted_zone" {
  type = string
}

variable "hosted_zone_arn" {
  type = string
}

# TODO: investigate why we need this as this is not clear to me
variable "hostname" {
  type = string
}
