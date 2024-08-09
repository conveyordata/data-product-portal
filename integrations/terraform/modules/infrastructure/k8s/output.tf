output "cluster_name" {
  value = module.eks.cluster_name
}

output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "oidc_provider_arn" {
  value = module.eks.oidc_provider_arn
}

output "cluster_node_role_arn" {
  value = module.eks.eks_managed_node_groups["initial_node_group"].iam_role_arn
}

output "cluster_node_role_name" {
  value = module.eks.eks_managed_node_groups["initial_node_group"].iam_role_name
}

output "node_security_group_id" {
  value = module.eks.node_security_group_id
}
