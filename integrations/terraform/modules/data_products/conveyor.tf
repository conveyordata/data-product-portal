resource "conveyor_project" "project" {
  count = var.conveyor_enabled ? 1 : 0
  name  = var.data_product_name

  description          = var.data_product_config.description
  default_iam_identity = "${var.prefix}-${local.aws_iam}-${var.data_product_name}-{{ .Env }}-${var.account_name}"

  default_ide_config {
    build_steps {
      name = "AWS cli"
      cmd  = <<-EOT
        sudo apt update
        sudo apt install -y unzip less
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
        rm -rf awscliv2.zip ./aws
        EOT
    }
  }

  lifecycle {
    prevent_destroy = true
  }
}
