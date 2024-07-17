locals {
  conveyor_oidc_provider_arn = "arn:aws:iam::${var.aws_account_id}:oidc-provider/${replace(var.environment_config.conveyor_oidc_provider_url, "https://", "")}"
}

data "aws_iam_policy_document" "project_arp" {
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
        "system:serviceaccount:${var.environment}:${replace(var.project_name, "_", ".")}-????????-????-????-????-????????????"
      ]
    }

    principals {
      identifiers = [local.conveyor_oidc_provider_arn]
      type        = "Federated"
    }
  }
}

resource "aws_iam_role" "project" {
  name               = "${var.prefix}-${local.aws_iam}-${var.project_name}-${var.environment}-${var.account_name}"
  assume_role_policy = data.aws_iam_policy_document.project_arp.json
}

resource "aws_iam_role_policy_attachment" "project_service" {
  role       = aws_iam_role.project.name
  policy_arn = aws_iam_policy.service_access.arn
}

resource "aws_iam_role_policy_attachment" "project_read" {
  count = length(var.read_data_access_policy_arns)

  role       = aws_iam_role.project.name
  policy_arn = var.read_data_access_policy_arns[count.index]
}

resource "aws_iam_role_policy_attachment" "project_write" {
  count = length(var.write_data_access_policy_arns)

  role       = aws_iam_role.project.name
  policy_arn = var.write_data_access_policy_arns[count.index]
}
