locals {
  # This prefix will be used for all of your created resources
  prefix = "portal"
  # Name of the AWS account
  account_name = "data-platform"
  # Region where you want to deploy resources to
  aws_region = "eu-west-1"

  # Choose whether you want to set up Conveyor integrations
  conveyor_enabled = false

  # Tags that will be set for all AWS services
  tags = {
    Environment = local.account_name
    Project     = local.prefix
  }
}
