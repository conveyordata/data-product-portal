locals {
  external_dns_values = <<EOF
image:
  registry: public.ecr.aws
  repository: bitnami/external-dns
provider: aws
aws:
  region: ${var.aws_region}
  zoneType: private
serviceAccount:
  name: external-dns
  annotations:
    eks.amazonaws.com/role-arn: ${module.external_dns_irsa_role.iam_role_arn}
EOF
}

module "external_dns_irsa_role" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"

  role_name                     = "${var.prefix}-${local.aws_iam}-external-dns-${var.account_name}"
  attach_external_dns_policy    = true
  external_dns_hosted_zone_arns = [var.account_config.hosted_zone_arn]

  oidc_providers = {
    ex = {
      provider_arn               = var.k8s_config.oidc_provider_arn
      namespace_service_accounts = ["kube-system:external-dns"]
    }
  }
}

resource "helm_release" "external_dns" {
  name       = "external-dns"
  repository = "https://charts.bitnami.com/bitnami"
  chart      = "external-dns"
  version    = "6.13.2"
  namespace  = "kube-system"
  values     = [local.external_dns_values]
}
