resource "databricks_catalog" "data_product_catalog" {
  for_each = var.data_product_glossary
  provider = databricks.workspace
  name = "${each.key}__${local.environment_name_map[var.environment]}"
  isolation_mode = "ISOLATED"
}
