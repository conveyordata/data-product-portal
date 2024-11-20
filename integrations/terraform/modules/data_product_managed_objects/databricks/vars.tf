variable "prefix" {}

variable "data_outputs" {
  type = map(object({
    s3 = list(object({
      bucket_identifier = string
      suffix            = string
      path              = string
    }))
    glue = list(object({
      database_identifier = string
      database_suffix     = string
      table               = string
      bucket_identifier   = string
      database_path       = string
      table_path          = string
    }))
    dbx = list(object({
      schema_identifier = string
      table             = string
      bucket_identifier = string
      schema_path       = string
      table_path        = string
    }))
    owner = string
  }))
}

variable "datasets" {
  type = map(object({
    data_outputs = list(string)
  }))
}

variable "data_product_glossary" {
  type = map(object({
    description   = string
    read_datasets = list(string)
    users         = list(string)
    services = object({
      console         = bool
      ssm             = bool
      athena          = bool
      create_iam_user = bool
    })
    business_unit = string
  }))
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
    dbx_account_id             = string
    dbx_metastore_id           = string
    dbx_credential_name        = string
    business_units             = list(string)
  })
}
