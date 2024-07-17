variable "prefix" {}
variable "aws_region" {}
variable "aws_account_id" {}
variable "account_name" {}

variable "environment" {}

variable "environment_config" {
  type = object({
    datalake = object({
      bucket      = string
      bucket_arn  = string
      kms_key_arn = string
    })
    logs = object({
      bucket      = string
      bucket_arn  = string
      kms_key_arn = string
    })
    ingress_enabled = bool
    ingress = object({
      bucket      = string
      bucket_arn  = string
      kms_key_arn = string
    })
    egress_enabled = bool
    egress = object({
      bucket      = string
      bucket_arn  = string
      kms_key_arn = string
    })
    can_read_from              = list(string)
    conveyor_oidc_provider_url = string
    database_glossary = map(object({
      glue_database = string
      s3            = string
    }))
  })
}

variable "project_name" {}

variable "project_config" {
  type = object({
    description      = string
    read_data_topics = list(string)
    services = object({
      console         = bool
      ssm             = bool
      athena          = bool
      create_iam_user = bool
    })
  })
}

variable "data_ids" {
  type = map(object({
    s3 = list(object({
      bucket_name = string
      path        = string
    }))
    glue  = list(string)
    owner = list(string)
  }))
}

variable "data_topics" {
  type = map(object({
    data_ids = list(string)
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

variable "project_folder_prefix" {
  default = "project"
}
