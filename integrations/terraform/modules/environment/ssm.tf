resource "aws_ssm_parameter" "datalake_bucket" {
  name  = "/platform/public/${var.prefix}/${var.env}/datalake/bucket"
  type  = "String"
  value = aws_s3_bucket.datalake.id
}

resource "aws_ssm_parameter" "datalake_kms_key_arn" {
  name  = "/platform/public/${var.prefix}/${var.env}/datalake/kms_key"
  type  = "String"
  value = aws_kms_key.datalake.arn
}

resource "aws_ssm_parameter" "logs_bucket" {
  name  = "/platform/public/${var.prefix}/${var.env}/logs/bucket"
  type  = "String"
  value = aws_s3_bucket.logs.id
}

resource "aws_ssm_parameter" "ingress_bucket" {
  count = var.ingress ? 1 : 0

  name  = "/platform/public/${var.prefix}/${var.env}/ingress/bucket"
  type  = "String"
  value = aws_s3_bucket.ingress[0].id
}

resource "aws_ssm_parameter" "ingress_kms_key_arn" {
  count = var.ingress ? 1 : 0

  name  = "/platform/public/${var.prefix}/${var.env}/ingress/kms_key"
  type  = "String"
  value = aws_kms_key.ingress[0].arn
}

resource "aws_ssm_parameter" "egress_bucket" {
  count = var.egress ? 1 : 0

  name  = "/platform/public/${var.prefix}/${var.env}/egress/bucket"
  type  = "String"
  value = aws_s3_bucket.egress[0].id
}

resource "aws_ssm_parameter" "egress_kms_key_arn" {
  count = var.egress ? 1 : 0

  name  = "/platform/public/${var.prefix}/${var.env}/egress/kms_key"
  type  = "String"
  value = aws_kms_key.egress[0].arn
}
