output "service_policy_arns" {
  value = [aws_iam_policy.service_access.arn]
}
