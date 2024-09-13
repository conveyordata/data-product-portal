locals {
  mandatory_tags = merge(local.tags, {
    Terraform = "true"
  })
  database_glossary_raw = yamldecode(file("${path.root}/config/data_glossary/database_glossary.yaml"))
  database_glossary = {
    for k, v in local.database_glossary_raw : k => {
      s3 = v["s3"]
    }
  }

  data_product_glossary_raw = yamldecode(file("${path.root}/config/data_product_glossary/data_product_glossary.yaml"))
  data_product_glossary = {
    for k, v in local.data_product_glossary_raw : k => {
      description   = try(v["description"], "")
      read_datasets = try(v["read_datasets"], [])
      services = {
        console         = try(v["services"]["console"], true)          # Console access enabled by default
        ssm             = try(v["services"]["ssm"], true)              # SSM access enabled by default
        athena          = try(v["services"]["athena"], true)           # Athena access enabled by default
        create_iam_user = try(v["services"]["create_iam_user"], false) # IAM user creation disabled by default
      }
    }
  }

  data_outputs_raw = yamldecode(file("${path.root}/config/data_glossary/data_outputs.yaml"))
  data_outputs = {
    for k, v in local.data_outputs_raw : k => {
      s3    = try(v["s3"], [])
      glue  = try(v["glue"], [])
      owner = try(v["owner"], [])
    }
  }

  datasets_raw = yamldecode(file("${path.root}/config/data_glossary/datasets.yaml"))
  datasets = {
    for k, v in local.datasets_raw : k => {
      data_outputs = v["data_outputs"]
    }
  }

  environments_raw = yamldecode((file("${path.root}/config/environment_configuration/environments.yaml")))
  environments = {
    for environment, config in local.environments_raw : environment => {
      aws_account_id = local.aws_account_id
      aws_region = local.aws_region
      can_read_from = []
      conveyor_oidc_provider_url = ""
      bucket_glossary = try(config["S3"], {})
      database_glossary = try(config["Glue"], {})
    }
  }
}
