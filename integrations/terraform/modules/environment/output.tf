output "datalake" {
  value = {
    bucket      = aws_s3_bucket.datalake.id
    bucket_arn  = aws_s3_bucket.datalake.arn
    kms_key_arn = aws_kms_key.datalake.arn
  }
}

output "logs" {
  value = {
    bucket      = aws_s3_bucket.logs.id
    bucket_arn  = aws_s3_bucket.logs.arn
    kms_key_arn = ""
  }
}

output "ingress_enabled" {
  value = var.ingress
}

output "ingress" {
  value = {
    bucket      = var.ingress ? aws_s3_bucket.ingress[0].id : ""
    bucket_arn  = var.ingress ? aws_s3_bucket.ingress[0].arn : ""
    kms_key_arn = var.ingress ? aws_kms_key.ingress[0].arn : ""
  }
}

output "egress_enabled" {
  value = var.egress
}

output "egress" {
  value = {
    bucket      = var.egress ? aws_s3_bucket.egress[0].id : ""
    bucket_arn  = var.egress ? aws_s3_bucket.egress[0].arn : ""
    kms_key_arn = var.egress ? aws_kms_key.egress[0].arn : ""
  }
}

output "can_read_from" {
  value = var.can_read_from
}

output "conveyor_oidc_provider_url" {
  value = var.conveyor_oidc_provider_url
}

output "database_glossary" {
  value = {
    for k, v in aws_glue_catalog_database.glue_database : k => {
      glue_database = v.name
      s3            = var.database_glossary[k].s3
    }
  }
}
