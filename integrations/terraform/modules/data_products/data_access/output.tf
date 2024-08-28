output "read_policy_arns" {
  value = concat([aws_iam_policy.policy_read_generic.arn], [for k, v in aws_iam_policy.policy_bucket_read : v.arn])
}

output "write_policy_arns" {
  value = concat([aws_iam_policy.policy_write_generic.arn, aws_iam_policy.policy_glue_write.arn],
  [for k, v in aws_iam_policy.policy_bucket_write : v.arn])
}
