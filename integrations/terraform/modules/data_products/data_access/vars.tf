variable "prefix" {}
variable "account_name" {}

variable "environment" {}

variable "environment_config" {
  type = object({
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
  })
}

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

variable "data_outputs" {
  type = map(object({
    s3 = list(object({
      bucket_identifier = string
      path              = string
    }))
    glue  = list(object({
      database_identifier = string
      table_prefixes      = list(string)
    }))
    owner = string
  }))
}

variable "datasets" {
  type = map(object({
    data_outputs = list(string)
  }))
}

variable "read_chunk_size" {
  type    = number
  default = 30
}

variable "write_chunk_size" {
  type    = number
  default = 30
}

variable "data_product_folder_prefix" {
  default = "data_product"
}
