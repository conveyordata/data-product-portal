resource "databricks_workspace_binding" "read_catalogs" {
  for_each = local.has_read_datasets ? toset(local.read_catalogs) : []
  provider = databricks.workspace
  securable_name = each.key
  workspace_id   = local.data_product_workspace
}

resource "databricks_workspace_binding" "write_catalog" {
  provider = databricks.workspace
  securable_name = local.data_product_catalog
  workspace_id   = local.data_product_workspace
}
