data "aws_iam_policy_document" "service_access" {
  source_policy_documents = flatten([
    [data.aws_iam_policy_document.permission_get_all_buckets.json],
    var.project_config.services.console ? [data.aws_iam_policy_document.permission_console_read.json] : [],
    var.project_config.services.ssm ? [data.aws_iam_policy_document.permission_ssm.json] : [],
    var.project_config.services.athena ? [data.aws_iam_policy_document.permission_athena.json] : []
  ])
}

resource "aws_iam_policy" "service_access" {
  name   = "${var.prefix}-${local.aws_iam}-${var.project_name}-service-${var.environment}-${var.account_name}"
  policy = data.aws_iam_policy_document.service_access.json
}
