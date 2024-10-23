variable "prefix" {}
variable "account_name" {}

variable "data_product_name" {}

variable "data_product_config" {
  type = object({
    description   = string
    read_datasets = list(string)
    services = object({
      console         = bool
      ssm             = bool
      athena          = bool
      create_iam_user = bool
    })
  })
}

variable "environment" {}

variable "environment_config" {
  type = object({
    aws_account_id             = string
    aws_region                 = string
    can_read_from              = list(string)
    conveyor_oidc_provider_url = string
    bucket_glossary = map(object({
      bucket_name = string
      bucket_arn  = string
      kms_key_arn = string
      is_default  = bool
    }))
  })
}

variable "read_data_access_policy_arns" {
  type = list(string)
}

variable "write_data_access_policy_arns" {
  type = list(string)
}

variable "service_policy_arns" {
  type = list(string)
}
