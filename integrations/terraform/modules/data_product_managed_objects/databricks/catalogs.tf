# Catalog per data product
resource "databricks_catalog" "data_product_catalog" {
  for_each = var.data_product_glossary

  provider = databricks.workspace

  name           = "${each.key}__${var.environment}"
  isolation_mode = "ISOLATED"
}
