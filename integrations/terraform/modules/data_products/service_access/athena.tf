locals {
  athena_output_location     = "s3://${local.default_bucket.bucket_name}/${var.athena_output_path_prefix}/${var.data_product_name}"
  athena_output_location_arn = "${local.default_bucket.bucket_arn}/${var.athena_output_path_prefix}/${var.data_product_name}"
  athena_workgroup           = "${var.data_product_name}-${var.environment}"
}

resource "aws_athena_workgroup" "athena" {
  name          = local.athena_workgroup
  description   = "Athena workgroup of the ${var.data_product_name} purpose in the ${var.environment} environment"
  state         = "ENABLED"
  force_destroy = true

  configuration {
    enforce_workgroup_configuration    = true
    bytes_scanned_cutoff_per_query     = 100 * 1024 * 1024 * 1024 # 100 GB Query cut off
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = local.athena_output_location

      encryption_configuration {
        encryption_option = "SSE_KMS"
        kms_key_arn       = local.default_bucket.kms_key_arn
      }
    }
  }
}
