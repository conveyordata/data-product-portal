# Athena
resource "aws_security_group" "endpoint_sg" {
  name        = "${var.prefix}-${local.aws_ec2}-${var.service}-endpoint"
  description = "Security group for ${var.service} endpoints"
  vpc_id      = var.vpc_id
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_ranges
  }
}

resource "aws_vpc_endpoint" "endpoint" {
  service_name        = "com.amazonaws.${var.aws_region}.${var.service}"
  vpc_id              = var.vpc_id
  vpc_endpoint_type   = "Interface"
  security_group_ids  = [aws_security_group.endpoint_sg.id]
  subnet_ids          = var.subnet_ids
  private_dns_enabled = true
}
