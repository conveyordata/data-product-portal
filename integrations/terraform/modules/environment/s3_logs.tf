resource "random_string" "logs" {
  length  = 6
  upper   = false
  numeric = false
  special = false

  lifecycle {
    prevent_destroy = true
  }
}

# TODO: Add bucket/endpoint policy
# TODO: Should logs be accessible from outside the VPC?
resource "aws_s3_bucket" "logs" {
  bucket = "${var.prefix}-${local.aws_s3}-logging-${var.env}-${var.account_name}-${random_string.logs.result}"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    id     = "move-to-infrequent-access"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    } # TODO: Should logs be moved to glacier and/or removed after a certain period?
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

resource "aws_s3_bucket_server_side_encryption_configuration" "logs" {
  bucket = aws_s3_bucket.logs.bucket

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket                  = aws_s3_bucket.logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "logs" {
  bucket = aws_s3_bucket.logs.id
  policy = data.aws_iam_policy_document.logs.json
}

data "aws_iam_policy_document" "logs" {
  statement {
    sid     = "DefaultLogsPermissions"
    effect  = "Allow"
    actions = ["s3:*"]
    resources = [
      "arn:aws:s3:::${aws_s3_bucket.logs.id}",
      "arn:aws:s3:::${aws_s3_bucket.logs.id}/*",
    ]

    principals {
      identifiers = [var.aws_account_id]
      type        = "AWS"
    }
  }

  # TODO: verify whether this works
  statement {
    sid     = "S3ServerAccessLogsPolicy"
    effect  = "Allow"
    actions = ["s3:PutObject"]
    principals {
      type        = "Service"
      identifiers = ["logging.s3.amazonaws.com"]
    }
    resources = [
      "arn:aws:s3:::${aws_s3_bucket.logs.id}/${var.s3_access_logs_prefix}*"
    ]
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [var.aws_account_id]
    }
  }
}
