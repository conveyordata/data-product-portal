locals {
  mandatory_tags = merge(local.tags, {
    Terraform = "true"
  })

  database_glossary_raw = yamldecode(file("${path.root}/config/database_glossary.yaml"))
  database_glossary = {
    for k, v in local.database_glossary_raw : k => {
      s3 = v["s3"]
    }
  }
}
