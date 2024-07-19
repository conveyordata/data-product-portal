resource "aws_iam_user" "user" {
  name          = "${var.data_product_name}-${var.environment}"
  force_destroy = true
}

resource "time_sleep" "wait_after_user_creation" {
  create_duration  = "5s"
  destroy_duration = "0s"
  depends_on       = [aws_iam_user.user]
}

resource "aws_iam_user_policy_attachment" "user_read_access" {
  count = length(var.read_data_access_policy_arns)

  user       = aws_iam_user.user.name
  policy_arn = var.read_data_access_policy_arns[count.index]

  depends_on = [time_sleep.wait_after_user_creation]
}

resource "aws_iam_user_policy_attachment" "user_write_access" {
  count = length(var.write_data_access_policy_arns)

  user       = aws_iam_user.user.name
  policy_arn = var.write_data_access_policy_arns[count.index]

  depends_on = [time_sleep.wait_after_user_creation]
}

resource "aws_iam_user_policy_attachment" "user_service_access" {
  count = length(var.service_policy_arns)

  user       = aws_iam_user.user.name
  policy_arn = var.service_policy_arns[count.index]

  depends_on = [time_sleep.wait_after_user_creation]
}
