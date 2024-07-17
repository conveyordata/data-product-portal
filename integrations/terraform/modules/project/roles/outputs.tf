output "project_role_arn" {
  value = aws_iam_role.project.arn
}

output "service_policy_arns" {
  value = [aws_iam_policy.service_access.arn]
}
