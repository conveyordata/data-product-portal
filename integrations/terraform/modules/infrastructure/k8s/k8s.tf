module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = var.cluster_name
  cluster_version = var.eks_version

  cluster_endpoint_public_access  = var.cluster_endpoint_public_access
  cluster_endpoint_private_access = var.cluster_endpoint_private_access

  # Extend node-to-node security group rules # this gave error as it already existed
  /*
  node_security_group_additional_rules = {
    ingress_self_all = {
      description = "Node to node all ports/protocols"
      protocol    = "-1"
      from_port   = 0
      to_port     = 0
      type        = "ingress"
      self        = true
    }
    egress_all = {
      description      = "Node all egress"
      protocol         = "-1"
      from_port        = 0
      to_port          = 0
      type             = "egress"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = ["::/0"]
    }
    ingress_allow_access_from_control_plane = {
      description                   = "Allow access from control plane to webhook port of AWS load balancer controller"
      type                          = "ingress"
      protocol                      = "tcp"
      from_port                     = 9443
      to_port                       = 9443
      source_cluster_security_group = true
    }
  }
  */

  cluster_addons = {
    coredns = {
      most_recent                 = true
      resolve_conflicts_on_create = "OVERWRITE"
      resolve_conflicts_on_update = "OVERWRITE"
    }
    kube-proxy = {
      most_recent                 = true
      resolve_conflicts_on_create = "OVERWRITE"
      resolve_conflicts_on_update = "OVERWRITE"
    }
    vpc-cni = {
      most_recent                 = true
      resolve_conflicts_on_create = "OVERWRITE"
      resolve_conflicts_on_update = "OVERWRITE"
    }
    # TODO: investigate whether this is actually needed?
    aws-ebs-csi-driver = {
      most_recent                 = true
      resolve_conflicts_on_create = "OVERWRITE"
      resolve_conflicts_on_update = "OVERWRITE"
    }
  }

  vpc_id                   = var.vpc_config.vpc_id
  subnet_ids               = [for k, v in var.vpc_config.non_routable_subnets : v.subnet_id]
  control_plane_subnet_ids = [for k, v in var.vpc_config.routable_subnets : v.subnet_id]

  # EKS Managed Node Group(s)
  eks_managed_node_group_defaults = {
    instance_types = ["m6i.xlarge", "m6a.xlarge", "m5.xlarge", "m5n.xlarge", "m5zn.xlarge"]
    disk_size      = 50
    ami_type       = "AL2_x86_64"
  }

  eks_managed_node_groups = {
    initial_node_group = {
      # By default, the module creates a launch template to ensure tags are propagated to instances, etc.,
      # so we need to disable it to use the default template provided by the AWS EKS managed node group service
      use_custom_launch_template = false
      min_size                   = 1
      max_size                   = 1
      desired_capacity           = 1
      capacity_type              = "ON_DEMAND"
    }
  }

  node_security_group_tags = {
    "karpenter.sh/discovery" = var.cluster_name
  }

  # aws-auth configmap
  manage_aws_auth_configmap = length(var.eks_admin_role_arns) == 0 ? false : true # true works for first apply, but break subsequent applies.

  aws_auth_roles = [
    for admin_role_arn in var.eks_admin_role_arns :
    {
      rolearn  = admin_role_arn
      username = "cluster-admin"
      groups   = ["system:masters"]
    }
  ]
  kms_key_administrators = var.eks_admin_role_arns
}

resource "aws_iam_role_policy_attachment" "ebs_node_policy_attachment" {
  role       = module.eks.eks_managed_node_groups["initial_node_group"].iam_role_name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
}
