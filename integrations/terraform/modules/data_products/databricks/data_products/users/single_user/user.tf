# resource "databricks_user" "data_product_user" {
#   provider  = databricks.mws
#   user_name = "${split("@", var.user)[0]}+${var.environment}-${var.data_product_name}-${var.prefix}@${split("@", var.user)[1]}"
#   disable_as_user_deletion = false
# }

data "databricks_user" "data_product_user" {
  provider = databricks.mws
  user_name = var.user
}

resource "databricks_group_member" "group_member" {
  provider  = databricks.mws
  count = length(var.access_groups)

  group_id  = var.access_groups[count.index]
  member_id = data.databricks_user.data_product_user.id
}
