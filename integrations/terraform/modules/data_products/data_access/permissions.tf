# The data lake list permission does not include get bucket location,
# because we assume it's always paired with getallbuckets.
data "aws_iam_policy_document" "permission_bucket_list" {
  statement {
    sid       = "S3BucketList"
    effect    = "Allow"
    actions   = ["s3:ListBucket"]
    resources = local.bucket_list
  }
}

data "aws_iam_policy_document" "permission_bucket_read" {
  for_each = local.chunked_read_paths
  statement {
    sid       = "S3BucketRead${each.key}"
    effect    = "Allow"
    actions   = local.aws_actions.s3.readonly
    resources = each.value
  }
}

data "aws_iam_policy_document" "permission_bucket_write" {
  for_each = local.chunked_write_paths
  statement {
    sid       = "S3BucketWrite${each.key}"
    effect    = "Allow"
    actions   = local.aws_actions.s3.readwrite
    resources = each.value
  }
}

data "aws_iam_policy_document" "permission_kms_read" {
  statement {
    sid       = "S3KMSRead"
    effect    = "Allow"
    actions   = local.aws_actions.kms.readonly
    resources = local.read_kms_keys
  }
}

data "aws_iam_policy_document" "permission_kms_write" {
  statement {
    sid       = "S3KMSWrite"
    effect    = "Allow"
    actions   = local.aws_actions.kms.readwrite
    resources = local.write_kms_keys
  }
}

data "aws_iam_policy_document" "permission_glue_read" {
  statement {
    sid    = "GlueReadDB"
    effect = "Allow"
    actions = [
      "glue:GetDatabase*",
      "glue:GetUserDefinedFunction*"
    ]

    resources = ["*"]
  }

  # TODO: make glue table read more specific, or allow for more "discoverability"?
  statement {
    sid    = "GlueReadTable"
    effect = "Allow"
    actions = [
      "glue:GetTable*",
      "glue:*GetPartition*",
    ]
    resources = [
      "arn:aws:glue:${var.aws_region}:${var.aws_account_id}:catalog",
      "arn:aws:glue:${var.aws_region}:${var.aws_account_id}:database/*",
      "arn:aws:glue:${var.aws_region}:${var.aws_account_id}:table/*/*",
    ]
  }
}

# TODO: make glue policies chunked as well, but will probably never hit...
data "aws_iam_policy_document" "permission_glue_write" {
  statement {
    sid    = "GlueWriteTable"
    effect = "Allow"
    actions = [
      "glue:*Table*",
      "glue:*Partition*",
    ]

    resources = concat(
      ["arn:aws:glue:${var.aws_region}:${var.aws_account_id}:catalog"],
      [for v in local.write_glue_databases : "arn:aws:glue:${var.aws_region}:${var.aws_account_id}:database/${v}"],
      [for v in local.write_glue_tables : "arn:aws:glue:${var.aws_region}:${var.aws_account_id}:table/${v}"],
    )
  }
}
