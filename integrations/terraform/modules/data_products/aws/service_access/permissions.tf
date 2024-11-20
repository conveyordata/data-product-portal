# Allow to list all buckets
data "aws_iam_policy_document" "permission_get_all_buckets" {
  statement {
    sid    = "DatalakeS3ListBuckets"
    effect = "Allow"
    actions = [
      "s3:ListAllMyBuckets",
      "s3:GetBucket*"
    ]
    resources = ["arn:aws:s3:::*"]
  }
}

# Console access policy
data "aws_iam_policy_document" "permission_console_read" {
  statement {
    sid    = "ConsoleReadAccess"
    effect = "Allow"
    actions = [
      "iam:Generate*",
      "iam:Get*",
      "iam:List*",
    ]
    resources = ["*"]
  }
}

data "aws_iam_policy_document" "permission_athena" {
  statement {
    sid    = "GlobalAthenaAccess"
    effect = "Allow"
    actions = [
      "athena:GetDataCatalog",
      "athena:GetDatabase",
      "athena:GetTableMetadata",
      "athena:ListDataCatalogs",
      "athena:ListDatabases",
      "athena:ListEngineVersions",
      "athena:ListTableMetadata",
      "athena:ListWorkGroups",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "WorkgroupAthenaAccess"
    effect = "Allow"
    actions = [
      "athena:Batch*",
      "athena:CreateNamedQuery",
      "athena:DeleteNamedQuery",
      "athena:Get*",
      "athena:List*",
      "athena:*QueryExecution",
    ]
    resources = [aws_athena_workgroup.athena.arn]
  }

  statement {
    sid    = "AthenaQueryListAccess"
    effect = "Allow"
    actions = [
      "s3:GetBucket*",
      "s3:ListBucket*",
    ]
    resources = ["${local.athena_output_location_arn}/*"]
  }

  statement {
    sid    = "AthenaQueryResultsAccess"
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:ListMultipartUploadParts",
      "s3:AbortMultipartUpload",
      "s3:PutObject",
    ]
    resources = ["${local.athena_output_location_arn}/*"]
  }

  statement {
    sid       = "AthenaQueryResultsKMSAccess"
    effect    = "Allow"
    actions   = local.aws_actions.kms.readwrite
    resources = [local.default_bucket.kms_key_arn]
  }
}

data "aws_iam_policy_document" "permission_ssm" {
  # Read access on common and project specific parameters
  statement {
    sid    = "CommonSSMParameterStoreAccess"
    effect = "Allow"
    actions = [
      "ssm:Describe*",
      "ssm:Get*",
      "ssm:List*",
    ]

    resources = [
      "arn:aws:ssm:${var.environment_config.aws_region}:${var.environment_config.aws_account_id}:parameter/platform/public/*",
      "arn:aws:ssm:${var.environment_config.aws_region}:${var.environment_config.aws_account_id}:parameter/data_product/${var.data_product_name}/*",
    ]
  }

  # DecribeParameters is an account-level permission, required for using the console
  # This permission does allow you to describe *all* the parameters...
  statement {
    sid    = "DescribeParameters"
    effect = "Allow"
    actions = [
      "ssm:DescribeParameters"
    ]
    resources = [
      "arn:aws:ssm:${var.environment_config.aws_region}:${var.environment_config.aws_account_id}:*"
    ]
  }

  # Read/write access on purpose-specific access
  statement {
    sid    = "SSMParameterStoreAccess"
    effect = "Allow"
    actions = [
      "ssm:Describe*",
      "ssm:Get*",
      "ssm:List*",
      "ssm:*Parameter*"
    ]

    resources = [
      "arn:aws:ssm:${var.environment_config.aws_region}:${var.environment_config.aws_account_id}:parameter/data_product/${var.data_product_name}/${var.environment}/*",
    ]
  }
}
