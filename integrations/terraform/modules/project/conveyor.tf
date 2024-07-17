resource "conveyor_project" "project" {
  count = var.conveyor_enabled ? 1 : 0
  name  = var.project_name

  description          = var.project_config.description
  default_iam_identity = "${var.prefix}-${local.aws_iam}-${var.project_name}-{{ .Env }}-${var.account_name}"

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

    build_steps {
      name = "AWS console via boto3"
      cmd  = <<-EOT
        sudo apt update
        pip install boto3

        cat << EOS > ~/.local/lib/toconsole.py
        ${file("../../modules/project/toconsole.py")}
        EOS

        cat << EOF > aws-console
        #!/bin/sh
        www-browser \$(python ~/.local/lib/toconsole.py)
        EOF
        chmod +x aws-console
        sudo mv aws-console /usr/bin/

      EOT
    }
  }

  lifecycle {
    prevent_destroy = true
  }
}
