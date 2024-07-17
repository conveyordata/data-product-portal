locals {
  athena_output_location     = "s3://${var.environment_config.datalake.bucket}/${var.athena_output_path_prefix}/${var.project_name}"
  athena_output_location_arn = "${var.environment_config.datalake.bucket_arn}/${var.athena_output_path_prefix}/${var.project_name}"
  athena_workgroup           = "${var.project_name}-${var.environment}"
}

resource "aws_athena_workgroup" "athena" {
  name          = local.athena_workgroup
  description   = "Athena workgroup of the ${var.project_name} purpose in the ${var.environment} environment"
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
        kms_key_arn       = var.environment_config.datalake.kms_key_arn
      }
    }
  }
}
