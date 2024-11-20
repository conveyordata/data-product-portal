locals {
  prefix         = "portal"
  aws_account_id = "012345678901"
  account_name   = "data-platform"
  aws_region     = "eu-west-1"

  dbx_account_id           = "UUID"
  dbx_metastore_id         = "UUID"
  dbx_catalog_name         = "catalag"
  dbx_credential_name      = "dbx-unity-catalog-access"
  databricks_workspace_url = "https://dbc-*.cloud.databricks.com/"

  workspaces_config = {
    root = {
      url = "https://dbc-*.cloud.databricks.com/"
      id  = "0123456789012345"
      environment = "root"
    }
    business-unit-1-dev = {
      url = "https://dbc-*.cloud.databricks.com/"
      id  = "0123456789012345"
      environment = "development"
    }
    business-unit-1-prd = {
      url = "https://dbc-*.cloud.databricks.com/"
      id  = "0123456789012345"
      environment = "production"
    }
    business-unit-2-dev = {
      url = "https://dbc-*.cloud.databricks.com/"
      id  = "0123456789012345"
      environment = "development"
    }
    business-unit-2-prd = {
      url = "https://dbc-*.cloud.databricks.com/"
      id  = "0123456789012345"
      environment = "production"
    }
  }

  tags = {
    prefix       = local.prefix
    account_name = local.account_name
  }
}
