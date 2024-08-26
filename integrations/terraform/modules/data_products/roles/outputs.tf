output "data_product_role_arn" {
  value = aws_iam_role.data_product.arn
}

output "service_policy_arns" {
  value = [aws_iam_policy.service_access.arn]
}
