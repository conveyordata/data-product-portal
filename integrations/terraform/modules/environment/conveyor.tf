resource "conveyor_environment" "environment" {
  count = var.conveyor_enabled ? 1 : 0
  name  = var.env

  deletion_protection = true
  instance_lifecycle  = "on-demand"

  lifecycle {
    prevent_destroy = true
  }
}
