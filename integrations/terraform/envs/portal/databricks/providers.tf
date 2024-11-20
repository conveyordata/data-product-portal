terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    databricks = {
      source = "databricks/databricks"
    }
  }
}

provider "aws" {
  region              = local.aws_region
  allowed_account_ids = [local.aws_account_id]
  default_tags {
    tags = local.mandatory_tags
  }
}

data "aws_ssm_parameter" "databricks_client_id" {
  name = "/dbx/service_principles/admin/client-id"
}

data "aws_ssm_parameter" "databricks_secret" {
  name = "/dbx/service_principles/admin/secret"
}


// initialize provider in "MWS" mode for account-level resources
provider "databricks" {
  alias         = "mws"
  client_id     = data.aws_ssm_parameter.databricks_client_id.value
  client_secret = data.aws_ssm_parameter.databricks_secret.value
  account_id    = local.dbx_account_id
  host          = "https://accounts.cloud.databricks.com"
}
// Root workspace provider
provider "databricks" {
  alias         = "root-workspace"
  host          = local.workspaces_config["root"]["url"]
  client_id     = data.aws_ssm_parameter.databricks_client_id.value
  client_secret = data.aws_ssm_parameter.databricks_secret.value
}
// Workspace providers
provider "databricks" {
  alias         = "workspace-business-unit-1-dev"
  host          = local.workspaces_config["business-unit-1-dev"]["url"]
  client_id     = data.aws_ssm_parameter.databricks_client_id.value
  client_secret = data.aws_ssm_parameter.databricks_secret.value
}
provider "databricks" {
  alias         = "workspace-business-unit-1-prd"
  host          = local.workspaces_config["business-unit-1-prd"]["url"]
  client_id     = data.aws_ssm_parameter.databricks_client_id.value
  client_secret = data.aws_ssm_parameter.databricks_secret.value
}
provider "databricks" {
  alias         = "workspace-business-unit-2-dev"
  host          = local.workspaces_config["business-unit-1-dev"]["url"]
  client_id     = data.aws_ssm_parameter.databricks_client_id.value
  client_secret = data.aws_ssm_parameter.databricks_secret.value
}
provider "databricks" {
  alias         = "workspace-business-unit-2-prd"
  host          = local.workspaces_config["business-unit-2-prd"]["url"]
  client_id     = data.aws_ssm_parameter.databricks_client_id.value
  client_secret = data.aws_ssm_parameter.databricks_secret.value
}
