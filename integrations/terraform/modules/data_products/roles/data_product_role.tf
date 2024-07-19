locals {
  conveyor_oidc_provider_arn = "arn:aws:iam::${var.aws_account_id}:oidc-provider/${replace(var.environment_config.conveyor_oidc_provider_url, "https://", "")}"
}

data "aws_iam_policy_document" "data_product_arp" {
  statement {
    sid     = "DefaultAccountAssumeRolePolicy"
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "AWS"
      identifiers = [var.aws_account_id]
    }
  }

  statement {
    sid     = "ConveyorWorkerAssumeRoleWebIdentityV2"
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    condition {
      variable = "${replace(var.environment_config.conveyor_oidc_provider_url, "https://", "")}:sub"
      test     = "StringLike"
      values = [
        "system:serviceaccount:${var.environment}:${replace(var.data_product_name, "_", ".")}-????????-????-????-????-????????????"
      ]
    }

    principals {
      identifiers = [local.conveyor_oidc_provider_arn]
      type        = "Federated"
    }
  }
}

resource "aws_iam_role" "data_product" {
  name               = "${var.prefix}-${local.aws_iam}-${var.data_product_name}-${var.environment}-${var.account_name}"
  assume_role_policy = data.aws_iam_policy_document.data_product_arp.json
}

resource "aws_iam_role_policy_attachment" "data_product_service" {
  role       = aws_iam_role.data_product.name
  policy_arn = aws_iam_policy.service_access.arn
}

resource "aws_iam_role_policy_attachment" "data_product_read" {
  count = length(var.read_data_access_policy_arns)

  role       = aws_iam_role.data_product.name
  policy_arn = var.read_data_access_policy_arns[count.index]
}

resource "aws_iam_role_policy_attachment" "data_product_write" {
  count = length(var.write_data_access_policy_arns)

  role       = aws_iam_role.data_product.name
  policy_arn = var.write_data_access_policy_arns[count.index]
}
