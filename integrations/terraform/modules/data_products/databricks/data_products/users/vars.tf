variable "prefix" {}

variable "data_product_name" {}

variable "data_product_config" {
  type = object({
    description   = string
    read_datasets = list(string)
    users = list(string)
    services = object({
      console         = bool
      ssm             = bool
      athena          = bool
      create_iam_user = bool
    })
    business_unit = string
  })
}

variable "environment" {}

variable "environment_config" {
  type = object({
    aws_account_id = string
    aws_region     = string
    bucket_glossary = map(object({
      bucket_name = string
      bucket_arn  = string
      kms_key_arn = string
      is_default  = bool
    }))
    can_read_from              = list(string)
    conveyor_oidc_provider_url = string
    dbx_account_id    = string
    dbx_metastore_id  = string
    dbx_credential_name = string
    dbx_env_cluster_params = object({
      autotermination_minutes = optional(number)
      spark_version           = optional(string)
      node_type_id            = optional(string)
      data_security_mode      = optional(string)
      num_workers             = optional(number)
    })
    business_units = list(string)
  })
}

variable "data_access_groups" {
  type = object({
    write_access_group = string
    read_access_group  = string
  })
}

variable "service_access_groups" {
  type = object({
    service_access_group = string
  })
}
