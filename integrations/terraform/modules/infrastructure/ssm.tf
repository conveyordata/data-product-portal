resource "aws_ssm_parameter" "jump_host_id" {
  count = var.infrastructure_config.create_jump_host ? 1 : 0

  name  = "/platform/public/jump_host_id"
  type  = "String"
  value = aws_instance.jump_host[0].id
}
