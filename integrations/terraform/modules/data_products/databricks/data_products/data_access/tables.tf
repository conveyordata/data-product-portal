# locals {
#     // DBX-native (Tables)
#     write_tables = distinct(
#         [for output_id, data_output in var.data_outputs : output_id if data_output.owner == var.data_product_name && contains(local.dbx_tables, output_id)],
#     )
#     read_tables = distinct(concat(
#         [for output_id in local.read_datasets_items: output_id if contains(local.dbx_tables, output_id)],
#         local.write_tables
#     ))
# }
# resource "databricks_grant" "table_read_access"{
#     provider = databricks.workspace

#     for_each = toset(local.read_tables)

#     table = each.value
#     principal = databricks_group.read_access_group.display_name
#     privileges = local.table_read_permissions
# }

# resource "databricks_grant" "table_write_access"{
#     provider = databricks.workspace

#     for_each = toset(local.write_tables)

#     table = each.value
#     principal = databricks_group.write_access_group.display_name
#     privileges = local.table_write_permissions
# }
