variable "prefix" {}
variable "account_name" {}

variable "data_product_name" {
  validation {
    condition     = strcontains(var.data_product_name, "_") == false
    error_message = "Data product names should not contain _"
  }
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
    aws_account_id = string
    aws_region = string
    bucket_glossary = map(object({
      bucket_name = string
      bucket_arn  = string
      kms_key_arn = string
      is_default = bool
    }))
    can_read_from              = list(string)
    conveyor_oidc_provider_url = string
    database_glossary = map(object({
      glue_database_name = string
      # Path on the default bucket
      s3_path            = string
    }))
  }))
}

variable "data_outputs" {
  type = map(object({
    s3 = list(object({
      bucket_identifier = string
      path        = string
    }))
    glue  = list(string)
    owner = list(string)
  }))
}

variable "datasets" {
  type = map(object({
    data_outputs = list(string)
  }))
}

variable "conveyor_enabled" {}
