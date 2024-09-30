terraform {
  required_version = "~> 1.9.2"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    conveyor = {
      source = "datamindedbe/conveyor"
    }
  }
}

provider "aws" {
  region              = local.aws_region
  allowed_account_ids = distinct([for env, config in local.environments : config.aws_account_id])
  default_tags {
    tags = local.mandatory_tags
  }
}
