locals {
  # Extract glossary
  bucket_glossary = var.environment_config.bucket_glossary

  glue_outputs = { for k, v in var.data_outputs : k => v.glue[0] if length(v.glue) > 0 }

  glue_databases = distinct([for id, glue in local.glue_outputs : glue.database])
  glue_database_suffixes = {
    for database in local.glue_databases : database => distinct([for _, glue in local.glue_outputs : glue.suffix if glue.database == database])
  }
  glue_database_names = {
    for database, suffixes in local.glue_database_suffixes : database => {
      for suffix in suffixes : suffix =>
      (suffix == "" ? "${var.prefix}_${var.environment}_${database}" : "${var.prefix}_${var.environment}_${database}__${suffix}")
    }
  }

  create_glue_databases = merge([for _, glue in local.glue_outputs : {
    "${glue.database}_${glue.suffix}" = {
      database_name = local.glue_database_names[glue.database][glue.suffix]
      database_uri  = "s3://${local.bucket_glossary[glue.bucket_identifier].bucket_name}/${glue.database_path}"
    }
  }]...)
}
