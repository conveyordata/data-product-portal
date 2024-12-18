variable "prefix" {}
variable "account_name" {}

variable "data_product_name" {
}

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

variable "environments" {
  type = map(object({
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
  }))
}

variable "managed_objects" {
  # Per environment
  type = map(object({
    # database_glossary[database][suffix] => database_name
    database_glossary = map(map(string))
  }))
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
      catalog_path       = string
      catalog            = string
      table              = string
      table_path         = string
    }))
    owner = string
  }))
}

variable "datasets" {
  type = map(object({
    data_outputs = list(string)
  }))
}

variable "conveyor_enabled" {}
