variable "prefix" {}

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

variable "data_outputs" {
  type = map(object({
    s3 = list(object({
      bucket_identifier = string
      suffix            = string
      path              = string
    }))
    glue = list(object({
      database          = string
      suffix            = string
      table             = string
      bucket_identifier = string
      database_path     = string
      table_path        = string
    }))
    dbx = list(object({
      schema            = string
      suffix            = string
      bucket_identifier = string
      schema_path       = string
    }))
    owner = string
  }))
}
