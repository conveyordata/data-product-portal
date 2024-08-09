resource "random_string" "ingress" {
  count = var.ingress ? 1 : 0

  length  = 6
  upper   = false
  numeric = false
  special = false

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_kms_key" "ingress" {
  count = var.ingress ? 1 : 0

  description = "Key to encrypt the ingress bucket"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_kms_alias" "ingress" {
  count = var.ingress ? 1 : 0

  name          = "alias/${var.prefix}-${local.aws_kms}-${local.aws_s3}-ingress-key-${var.env}-${var.account_name}"
  target_key_id = aws_kms_key.ingress[0].id
}

resource "aws_s3_bucket" "ingress" {
  count = var.ingress ? 1 : 0

  bucket = "${var.prefix}-${local.aws_s3}-ingress-${var.env}-${var.account_name}-${random_string.ingress[0].result}"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "ingress" {
  count = var.ingress ? 1 : 0

  bucket = aws_s3_bucket.ingress[0].id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_logging" "ingress" {
  count = var.ingress ? 1 : 0

  bucket        = aws_s3_bucket.ingress[0].id
  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "${var.s3_access_logs_prefix}/ingress/"
}

resource "aws_s3_bucket_lifecycle_configuration" "ingress" {
  count = var.ingress ? 1 : 0

  bucket = aws_s3_bucket.ingress[0].id

  rule {
    id     = "Expire-30-days-and-NonCurrent-1-day"
    status = "Enabled"

    expiration {
      days = 30
    }

    noncurrent_version_expiration {
      noncurrent_days = 7
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

resource "aws_s3_bucket_server_side_encryption_configuration" "ingress" {
  count = var.ingress ? 1 : 0

  bucket = aws_s3_bucket.ingress[0].bucket

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.ingress[0].arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "ingress" {
  count = var.ingress ? 1 : 0

  bucket                  = aws_s3_bucket.ingress[0].id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


resource "aws_s3_bucket_policy" "ingress" {
  count = var.ingress ? 1 : 0

  bucket = aws_s3_bucket.ingress[0].id
  policy = data.aws_iam_policy_document.ingress.json
}

data "aws_iam_policy_document" "ingress" {
  # Everyone with credentials in our account can do everything from everywhere, except reading object data (see below).
  statement {
    sid     = "DefaultIngressPermissions"
    effect  = "Allow"
    actions = ["s3:*"]
    resources = [
      "arn:aws:s3:::${aws_s3_bucket.ingress[0].id}",
      "arn:aws:s3:::${aws_s3_bucket.ingress[0].id}/*",
    ]

    principals {
      identifiers = [var.aws_account_id]
      type        = "AWS"
    }
  }

  # You may only get objects from the ingress bucket from the VPC
  dynamic "statement" {
    for_each = var.datalake_vpc_restricted ? toset(["0"]) : toset([])
    content {
      sid    = "AccessIngressFromVPCEndpointOnly"
      effect = "Deny"
      actions = [
        "s3:GetObject"
      ]
      resources = [
        "arn:aws:s3:::${aws_s3_bucket.ingress[0].id}",
        "arn:aws:s3:::${aws_s3_bucket.ingress[0].id}/*",
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
    }
  }

  statement {
    sid     = "DenyUnsecureTransport"
    effect  = "Deny"
    actions = ["s3:*"]
    resources = [
      "arn:aws:s3:::${aws_s3_bucket.ingress[0].id}",
      "arn:aws:s3:::${aws_s3_bucket.ingress[0].id}/*",
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
  # See s3_datalake.tf for more details
  statement {
    sid    = "DenyUnencrypted"
    effect = "Deny"
    actions = [
      "s3:PutObject",
    ]
    resources = [
      "arn:aws:s3:::${aws_s3_bucket.ingress[0].id}/*",
    ]

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

  statement {
    sid    = "DenyNonDefaultKey"
    effect = "Deny"
    actions = [
      "s3:PutObject",
    ]
    resources = [
      "arn:aws:s3:::${aws_s3_bucket.ingress[0].id}/*",
    ]

    condition {
      test     = "StringNotEqualsIfExists"
      variable = "s3:x-amz-server-side-encryption-aws-kms-key-id"
      values   = [aws_kms_key.ingress[0].arn]
    }

    principals {
      identifiers = ["*"]
      type        = "AWS"
    }
  }
}
