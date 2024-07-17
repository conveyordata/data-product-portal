data "aws_iam_policy_document" "policy_read_generic" {
  source_policy_documents = [
    data.aws_iam_policy_document.permission_bucket_list.json,
    data.aws_iam_policy_document.permission_kms_read.json,
    # Glue read policies are currently generic
    data.aws_iam_policy_document.permission_glue_read.json
  ]
}

resource "aws_iam_policy" "policy_read_generic" {
  name   = "${var.prefix}-${local.aws_iam}-${var.project_name}-read-generic-${var.environment}-${var.account_name}"
  policy = data.aws_iam_policy_document.policy_read_generic.json
}

resource "aws_iam_policy" "policy_bucket_read" {
  for_each = data.aws_iam_policy_document.permission_bucket_read

  name   = "${var.prefix}-${local.aws_iam}-${var.project_name}-bucket-read-${each.key}-${var.environment}-${var.account_name}"
  policy = each.value.json
}

data "aws_iam_policy_document" "policy_write_generic" {
  source_policy_documents = [
    data.aws_iam_policy_document.permission_bucket_list.json,
    data.aws_iam_policy_document.permission_kms_write.json
  ]
}

resource "aws_iam_policy" "policy_write_generic" {
  name   = "${var.prefix}-${local.aws_iam}-${var.project_name}-write-generic-${var.environment}-${var.account_name}"
  policy = data.aws_iam_policy_document.policy_write_generic.json
}

resource "aws_iam_policy" "policy_bucket_write" {
  for_each = data.aws_iam_policy_document.permission_bucket_write

  name   = "${var.prefix}-${local.aws_iam}-${var.project_name}-bucket-write-${each.key}-${var.environment}-${var.account_name}"
  policy = each.value.json
}

resource "aws_iam_policy" "policy_glue_write" {
  name = "${var.prefix}-${local.aws_iam}-${var.project_name}-glue-write-${var.environment}-${var.account_name}"

  policy = data.aws_iam_policy_document.permission_glue_write.json
}
