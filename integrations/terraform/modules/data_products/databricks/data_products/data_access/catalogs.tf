locals {
  read_dbx_data_products = distinct([
    for data_output_id in local.read_datasets_items :
    var.data_outputs[data_output_id].owner if contains(local.dbx_outputs, data_output_id)
  ])

  include_catalogs = distinct([
    for data_product, catalog in var.managed_objects.data_product_catalogs :
    catalog if contains(local.read_dbx_data_products, data_product) || data_product == var.data_product_name
  ])
}

resource "databricks_grant" "dataproduct_catalog_access" {
  for_each = toset(local.include_catalogs)

  provider   = databricks.workspace
  catalog    = each.value
  principal  = databricks_group.read_access_group.display_name
  privileges = ["USE_CATALOG"]
}

# resource "databricks_grant" "external_data_catalog_access" {
#   provider   = databricks.workspace
#   catalog    = var.managed_objects.external_data_catalog
#   principal  = databricks_group.read_access_group.display_name
#   privileges = ["USE_CATALOG"]
# }
