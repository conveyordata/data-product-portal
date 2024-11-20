variable "prefix" {}

variable "data_product_name" {
  # validation {
  #   condition     = strcontains(var.data_product_name, "_") == false
  #   error_message = "Data product names should not contain _"
  # }
}

variable "data_product_config" {
  type = object({
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
  })
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

variable "managed_objects" {
  type = object({
    # Data Output -> Schema
    public_schemas = map(string)
    # Data Product -> Schema
    private_schemas = map(string)
    # External Data -> Schema
    external_data_schemas = map(string)
    # Tables -> Schema
    # public_tables = map(string)
    # # Data Output -> Url
    # external_locations = map(list(object({
    #   name = string
    #   url  = string
    # })))
    # Data Output -> External Volume
    external_volumes = map(string)
    # Single catalog for all external data outputs
    # external_data_catalog = string
    # Data product -> Catalog
    data_product_catalogs = map(string)
  })
}

variable "datasets" {
  type = map(object({
    data_outputs = list(string)
  }))
}

variable "business_unit" {}
variable "workspace_id" {}

variable "workspaces_config" {
  type = map(object({
    url = string
    id  = string
  }))
}

# variable "conveyor_enabled" {}
