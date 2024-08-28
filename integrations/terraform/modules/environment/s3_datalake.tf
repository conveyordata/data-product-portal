resource "aws_kms_key" "datalake" {
  description = "Key to encrypt the datalake bucket"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_kms_alias" "datalake" {
  name          = "alias/${var.prefix}-${local.aws_kms}-${local.aws_s3}-datalake-key-${var.env}-${var.account_name}"
  target_key_id = aws_kms_key.datalake.id
}

resource "random_string" "datalake" {
  length  = 6
  upper   = false
  numeric = false
  special = false

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket" "datalake" {
  bucket = "${var.prefix}-${local.aws_s3}-datalake-${var.env}-${var.account_name}-${random_string.datalake.result}"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "datalake" {
  bucket = aws_s3_bucket.datalake.bucket

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.datalake.arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "datalake" {
  bucket                  = aws_s3_bucket.datalake.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_logging" "datalake" {
  bucket        = aws_s3_bucket.datalake.id
  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "${var.s3_access_logs_prefix}/datalake/"
}

resource "aws_s3_bucket_versioning" "datalake" {
  bucket = aws_s3_bucket.datalake.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "datalake" {
  bucket = aws_s3_bucket.datalake.id
  # TODO: Enable lifecycle rules

  rule {
    # Athena query results should clean themselves automatically
    id     = "Athena"
    status = "Enabled"
    filter {
      prefix = "athena/"
    }

    expiration {
      days = 14
    }

    # we should not version cached Athena results, but unfortunately it is not possible to apply
    # versioning only to some prefixes in a bucket (or to exclude certain prefixes); we expire at minimum value of 1 day
    noncurrent_version_expiration {
      noncurrent_days = 1
    }
  }

  rule {
    id     = "Expire-Noncurrent-Versions"
    status = "Enabled"

    noncurrent_version_expiration {
      noncurrent_days = max(1, var.versioning_duration)
    }
  }

  rule {
    id     = "Default-Cleanup"
    status = "Enabled"

    abort_incomplete_multipart_upload {
      days_after_initiation = 3
    }

    expiration {
      expired_object_delete_marker = true
    }
  }
}

resource "aws_s3_bucket_policy" "datalake" {
  bucket = aws_s3_bucket.datalake.id
  policy = data.aws_iam_policy_document.datalake.json
}

data "aws_iam_policy_document" "datalake" {
  statement {
    sid     = "DefaultDatalakePermissions"
    effect  = "Allow"
    actions = ["s3:*"]
    resources = [
      "arn:aws:s3:::${aws_s3_bucket.datalake.id}",
      "arn:aws:s3:::${aws_s3_bucket.datalake.id}/*",
    ]

    principals {
      identifiers = [var.aws_account_id]
      type        = "AWS"
    }
  }

  # You may only read, delete and write data to and from the bucket from the VPC.
  dynamic "statement" {
    for_each = var.datalake_vpc_restricted ? toset(["0"]) : toset([])
    content {
      sid    = "AccessDatalakeFromVPCEndpointOnly"
      effect = "Deny"
      actions = [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ]
      resources = [
        "arn:aws:s3:::${aws_s3_bucket.datalake.id}/*",
      ]

      principals {
        identifiers = ["*"]
        type        = "AWS"
      }

      condition {
        test     = "StringNotEquals"
        variable = "aws:SourceVpce"
        values   = [var.vpc_config.s3_endpoint_id]
      }
      # Allow access to athena
      dynamic "condition" {
        for_each = var.athena_enabled ? toset(["0"]) : toset([])
        content {
          test     = "ForAllValues:StringNotEquals"
          variable = "aws:CalledVia"
          values   = ["athena.amazonaws.com"]
        }
      }

      dynamic "condition" {
        for_each = var.redshift_spectrum_enabled ? toset(["0"]) : toset([])
        content {
          test     = "StringNotEquals"
          variable = "aws:UserAgent"
          values   = ["AWS Redshift/Spectrum"]
        }
      }
    }
  }

  statement {
    sid     = "DenyUnsecureTransport"
    effect  = "Deny"
    actions = ["s3:*"]
    resources = [
      "arn:aws:s3:::${aws_s3_bucket.datalake.id}",
      "arn:aws:s3:::${aws_s3_bucket.datalake.id}/*",
    ]

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }

    principals {
      identifiers = ["*"]
      type        = "AWS"
    }
  }

  # All objects in the bucket should be encrypted by the bucket's KMS key.
  #   * If no encryption options are specified with the put request, the default bucket settings will be used.
  #   * It is possible to override the defaults by specifying encryption options in the put request.
  #     Source: https://docs.aws.amazon.com/AmazonS3/latest/userguide/default-bucket-encryption.html
  #   * It seems like the defaults are "added" to the put request only *after* IAM policy evaluation...
  #     Source: testing
  # The statements below will deny any put requests explicitly specifying encryption values different from the defaults.
  #
  # There's some oddities in evaluation with requests that do not specify or only partially specify encryption headers.
  #   * Put requests that set the x-amz-server-side-encryption header to aws:kms seem to always also have the
  #     x-amz-server-side-encryption-aws-kms-key-id property set during IAM evaluation (likely to  the empty string),
  #     even if the put request does not actually specify this value.
  #     (Verified on 30/7/2021 using the AWS CLI with --debug option)
  #   * The AWS policy simulator seems to always set the value of these headers (to empty strings).
  #
  # Deny all put operations that have the x-amz-server-side-encryption-header set to a value different from aws:kms
  # As an alternative to this, it is possible to deny the value AES256 if set since there's currently only two valid
  # values for x-amz-server-side-encryption
  #   https://aws.amazon.com/premiumsupport/knowledge-center/s3-bucket-store-kms-encrypted-objects/
  statement {
    sid    = "DenyUnencrypted"
    effect = "Deny"
    actions = [
      "s3:PutObject",
    ]
    resources = [
      "arn:aws:s3:::${aws_s3_bucket.datalake.id}/*",
    ]

    # Condition that is true when the variable is set (specified as "the value being null is false")
    condition {
      test     = "Null"
      variable = "s3:x-amz-server-side-encryption"
      values   = ["false"]
    }

    condition {
      test     = "StringNotEqualsIfExists"
      variable = "s3:x-amz-server-side-encryption"
      values   = ["aws:kms"]
    }

    principals {
      identifiers = ["*"]
      type        = "AWS"
    }
  }

  # Deny all put operations that specify usage of a KMS key that is not this bucket's default KMS key
  statement {
    sid    = "DenyNonDefaultKey"
    effect = "Deny"
    actions = [
      "s3:PutObject",
    ]
    resources = [
      "arn:aws:s3:::${aws_s3_bucket.datalake.id}/*",
    ]

    condition {
      test     = "StringNotEqualsIfExists"
      variable = "s3:x-amz-server-side-encryption-aws-kms-key-id"
      values   = [aws_kms_key.datalake.arn]
    }

    principals {
      identifiers = ["*"]
      type        = "AWS"
    }
  }
}
