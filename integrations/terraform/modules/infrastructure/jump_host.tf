# Security group
resource "aws_security_group" "jump_host" {
  count = var.infrastructure_config.create_jump_host ? 1 : 0

  name        = "${var.prefix}-${local.aws_security_group}-jumphost-${var.account_name}"
  description = "Security group for the jump host instance"
  vpc_id      = var.vpc_config.vpc_id
}

resource "aws_security_group_rule" "jump_host_egress" {
  count = var.infrastructure_config.create_jump_host ? 1 : 0

  security_group_id = aws_security_group.jump_host[0].id
  type              = "egress"
  protocol          = "-1"
  from_port         = 0
  to_port           = 65535
  cidr_blocks       = ["0.0.0.0/0"]
}

# TODO: need to restrict this later on
#resource "aws_security_group_rule" "jump_host_ingress" {
#  security_group_id = aws_security_group.jump_host.id
#  type              = "ingress"
#  protocol          = "-1"
#  from_port         = 0
#  to_port           = 65535
#  cidr_blocks = ["0.0.0.0/0"]
#}

# IAM role / instance profile
data "aws_iam_policy_document" "jump_host_arp" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "jump_host" {
  count = var.infrastructure_config.create_jump_host ? 1 : 0

  name               = "${var.prefix}-${local.aws_iam}-jumphost-${var.account_name}"
  assume_role_policy = data.aws_iam_policy_document.jump_host_arp.json
}

# TODO: give it restricted access
resource "aws_iam_role_policy_attachment" "jump_host" {
  count = var.infrastructure_config.create_jump_host ? 1 : 0

  role       = aws_iam_role.jump_host[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "jump_host" {
  count = var.infrastructure_config.create_jump_host ? 1 : 0

  name = "${var.prefix}-${local.aws_iam}-jumphost-${var.account_name}"
  role = aws_iam_role.jump_host[0].id
}

# EC2 configuration
data "aws_ami" "amzn-linux-2023-ami" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}

# Don't make conditional to keep key the same
resource "tls_private_key" "jump_host" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

locals {
  jump_host_key_pair_name = "${var.prefix}-${local.aws_ec2}-jumphost-${var.account_name}"
  routable_subnet_ids     = [for k, v in var.vpc_config.routable_subnets : v.subnet_id]
  jump_host_user_data     = <<EOF
#!/bin/bash
# Enable IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward
# Enable tunneling over SSH
echo "PermitTunnel yes" >> /etc/ssh/sshd_config
echo "GatewayPorts yes" >> /etc/ssh/sshd_config
systemctl reload sshd
EOF
}

resource "aws_key_pair" "jump_host" {
  count = var.infrastructure_config.create_jump_host ? 1 : 0

  key_name   = "${var.prefix}-${local.aws_ec2}-jumphost-${var.account_name}"
  public_key = tls_private_key.jump_host.public_key_openssh
}

resource "local_file" "jump_host_private_key" {
  count = var.infrastructure_config.create_jump_host ? 1 : 0

  filename        = "${var.prefix}-${local.aws_ec2}-jumphost.pem"
  file_permission = "0400"
  content         = tls_private_key.jump_host.private_key_pem
}

resource "aws_instance" "jump_host" {
  count = var.infrastructure_config.create_jump_host ? 1 : 0

  ami                         = data.aws_ami.amzn-linux-2023-ami.id
  instance_type               = "t2.micro"
  subnet_id                   = local.routable_subnet_ids[0]
  iam_instance_profile        = aws_iam_instance_profile.jump_host[0].id
  vpc_security_group_ids      = [aws_security_group.jump_host[0].id]
  key_name                    = aws_key_pair.jump_host[0].key_name
  user_data                   = local.jump_host_user_data
  user_data_replace_on_change = true

  tags = {
    Name = "${var.prefix}-${local.aws_ec2}-jumphost-${var.account_name}"
  }
}
