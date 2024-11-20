resource "databricks_group" "read_access_group" {
  provider = databricks.mws

  display_name = "${var.data_product_name}__${local.environment_name_map[var.environment]}__read_access_group"
}

resource "databricks_group" "write_access_group" {
  provider = databricks.mws

  display_name = "${var.data_product_name}__${local.environment_name_map[var.environment]}__write_access_group"
}
