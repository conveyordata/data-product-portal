locals {
  mandatory_tags = merge(local.tags, {
    Terraform = "true"
  })

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
      s3 = try([{
        bucket_identifier = v["s3"]["bucket"]
        suffix            = v["s3"]["suffix"]
        path              = v["s3"]["path"]
      }], [])
      glue = try([{
        database          = v["glue"]["database"]
        suffix            = v["glue"]["database_suffix"]
        table             = v["glue"]["table"]
        bucket_identifier = v["glue"]["bucket_identifier"]
        database_path     = v["glue"]["database_path"]
        table_path        = v["glue"]["table_path"]
      }], [])
      dbx = try([{
        catalog            = v["databricks"]["catalog"]
        schema            = v["databricks"]["schema"]
        bucket_identifier = v["databricks"]["bucket_identifier"]
        catalog_path       = v["databricks"]["catalog_path"]
        table              = v["databricks"]["table"]
        table_path         = v["databricks"]["table_path"]
      }], [])
      owner = try(v["owner"], "")
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
      aws_account_id             = config["aws"]["account_id"]
      aws_region                 = config["aws"]["region"]
      can_read_from              = try(config["aws"]["can_read_from"], [])
      conveyor_oidc_provider_url = ""
      bucket_glossary = {
        for s3 in try(config["aws"]["s3"], []) : s3["identifier"] => {
          bucket_name = s3["bucket_name"]
          bucket_arn  = s3["bucket_arn"]
          kms_key_arn = s3["kms_key_arn"]
          is_default  = s3["is_default"]
        }
      }
    }
  }
}
