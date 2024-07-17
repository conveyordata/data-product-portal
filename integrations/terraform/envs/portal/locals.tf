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

  project_glossary_raw = yamldecode(file("${path.root}/config/project_glossary/project_glossary.yaml"))
  project_glossary = {
    for k, v in local.project_glossary_raw : k => {
      description      = try(v["description"], "")
      read_data_topics = try(v["read_data_topics"], [])
      services = {
        console         = try(v["services"]["console"], true)          # Console access enabled by default
        ssm             = try(v["services"]["ssm"], true)              # SSM access enabled by default
        athena          = try(v["services"]["athena"], true)           # Athena access enabled by default
        create_iam_user = try(v["services"]["create_iam_user"], false) # IAM user creation disabled by default
      }
    }
  }

  data_ids_raw = yamldecode(file("${path.root}/config/data_glossary/data_ids.yaml"))
  data_ids = {
    for k, v in local.data_ids_raw : k => {
      s3    = try(v["s3"], [])
      glue  = try(v["glue"], [])
      owner = try(v["owner"], [])
    }
  }

  data_topics_raw = yamldecode(file("${path.root}/config/data_glossary/data_topics.yaml"))
  data_topics = {
    for k, v in local.data_topics_raw : k => {
      data_ids = v["data_ids"]
    }
  }
}
