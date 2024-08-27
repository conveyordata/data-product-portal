locals {
  aws_lb_controller_values = <<EOF
replicaCount: 1

serviceAccount:
  name: aws-load-balancer-controller
  annotations: {
     eks.amazonaws.com/role-arn: ${module.load_balancer_controller_irsa_role.iam_role_arn}
  }

resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 100m
    memory: 128Mi

enableCertManager: false
clusterName: ${var.k8s_config.cluster_name}
region: ${var.aws_region}
vpcId: ${var.vpc_config.vpc_id}

clusterSecretsPermissions:
  allowAllSecrets: true
EOF
}

module "load_balancer_controller_irsa_role" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"

  role_name                              = "${var.prefix}-${local.aws_iam}-load-balancer-controller-${var.account_name}"
  attach_load_balancer_controller_policy = true

  oidc_providers = {
    ex = {
      provider_arn               = var.k8s_config.oidc_provider_arn
      namespace_service_accounts = ["kube-system:aws-load-balancer-controller"]
    }
  }
}

# TODO: look into a solution to handle these tags generically
resource "aws_ec2_tag" "public_subnet_tag_public_elb" {
  for_each    = toset([for k, v in var.vpc_config.routable_subnets : v.subnet_id])
  resource_id = each.value
  key         = "kubernetes.io/role/elb"
  value       = "1"
}

resource "aws_ec2_tag" "public_subnet_tag_private_elb" {
  for_each    = toset([for k, v in var.vpc_config.routable_subnets : v.subnet_id])
  resource_id = each.value
  key         = "kubernetes.io/role/internal-elb"
  value       = "1"
}

resource "helm_release" "ingress-controller" {
  name       = "aws-ingress-controller"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  version    = var.alb_ingress_version
  namespace  = "kube-system"
  values     = [local.aws_lb_controller_values]
}
