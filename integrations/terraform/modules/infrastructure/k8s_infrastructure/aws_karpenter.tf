locals {
  aws_karpenter_values = <<EOF
replicas: 1
settings:
  aws:
    clusterName: ${var.k8s_config.cluster_name}
    clusterEndpoint: ${var.k8s_config.cluster_endpoint}
    defaultInstanceProfile: ${module.karpenter.instance_profile_name}
    interruptionQueueName: ${module.karpenter.queue_name}
    tags:
      "karpenter.sh/discovery": ${var.k8s_config.cluster_name}

serviceAccount:
  name: karpenter
  annotations:
    eks.amazonaws.com/role-arn: ${module.karpenter.irsa_arn}
EOF
}

# Sets up all aws infra we need for Karpenter to work
module "karpenter" {
  source = "terraform-aws-modules/eks/aws//modules/karpenter"

  cluster_name = var.k8s_config.cluster_name

  irsa_oidc_provider_arn          = var.k8s_config.oidc_provider_arn
  irsa_namespace_service_accounts = ["kube-system:karpenter"]

  create_iam_role      = false
  iam_role_arn         = var.k8s_config.cluster_node_role_arn
  irsa_use_name_prefix = false

  policies = {
    AmazonSSMManagedInstanceCore = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
    AmazonEBSCSIDriverPolicy     = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
  }
}

# Installs Karpenter on the cluster
resource "helm_release" "karpenter" {
  name       = "aws-karpenter"
  repository = "oci://public.ecr.aws/karpenter"
  chart      = "karpenter"
  version    = "v0.29.2"
  namespace  = "kube-system"
  values     = [local.aws_karpenter_values]
}

data "aws_eks_cluster" "cluster" {
  name = var.k8s_config.cluster_name
}

resource "aws_ec2_tag" "subnet" {
  for_each    = var.vpc_config.non_routable_subnets
  key         = "karpenter.sh/discovery"
  resource_id = each.value.subnet_id
  value       = var.k8s_config.cluster_name
}

# Create AWS node template so we know what subnet and security group to use for our started nodes
resource "kubernetes_manifest" "node_template" {
  manifest = {
    apiVersion = "karpenter.k8s.aws/v1alpha1"
    kind       = "AWSNodeTemplate"
    metadata = {
      name = "default"
    }
    spec = {
      subnetSelector = {
        # This subnet is tagged at creation time, during subnet creation
        "karpenter.sh/discovery" = var.k8s_config.cluster_name
      }
      securityGroupSelector = {
        # Use the default security group for the cluster created by the eks service
        "karpenter.sh/discovery" = var.k8s_config.cluster_name
      }
      blockDeviceMappings = [
        {
          deviceName = "/dev/xvda"
          ebs = {
            volumeType          = "gp3"
            volumeSize          = "50Gi"
            deleteOnTermination = true
          }
        }
      ]
    }
  }
  depends_on = [helm_release.karpenter]
}

# Create a default provisioner that will start Linux on demand nodes with 8 cores
resource "kubernetes_manifest" "provisioner" {
  manifest = {
    apiVersion = "karpenter.sh/v1alpha5"
    kind       = "Provisioner"
    metadata = {
      name = "default"
    }
    spec = {
      limits = {
        resources = {
          cpu = 128
        }
      }
      providerRef = {
        name = "default"
      }
      requirements = [
        {
          key      = "karpenter.k8s.aws/instance-category"
          operator = "In"
          values   = ["m"]
        },
        {
          key : "karpenter.k8s.aws/instance-generation"
          operator : "Gt"
          values : ["4"]
        },
        {
          key      = "karpenter.k8s.aws/instance-cpu"
          operator = "In"
          values   = ["8"]
        },
        {
          key      = "kubernetes.io/arch"
          operator = "In"
          values   = ["amd64"]
        },
        {
          key      = "kubernetes.io/os"
          operator = "In"
          values : ["linux"]
        },
        {
          key      = "karpenter.sh/capacity-type"
          operator = "In"
          # For some reason spot nodes only work on dev accounts
          values = contains(["dev", "int"], var.account_name) ? ["spot"] : ["on-demand"]
        }
      ]
      consolidation = {
        enabled = true
      }
    }
  }
  depends_on = [kubernetes_manifest.node_template]
}
