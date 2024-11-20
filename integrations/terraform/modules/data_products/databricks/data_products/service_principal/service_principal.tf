resource "databricks_service_principal" "data_product_service_principal" {
  provider = databricks.workspace
  display_name = "SP__${var.data_product_name}__${local.environment_name_map[var.environment]}"
}

resource "databricks_group_member" "group_member" {
  provider  = databricks.mws
  count = length(local.all_access_groups)

  group_id  = local.all_access_groups[count.index]
  member_id = databricks_service_principal.data_product_service_principal.id
}

resource "databricks_access_control_rule_set" "service_principal_rule_set" {
  name = "accounts/${local.account_id}/servicePrincipals/${databricks_service_principal.data_product_service_principal.application_id}/ruleSets/default"

  grant_rules {
    principals = [local.service_access_group_principal_id]
    role       = "roles/servicePrincipal.user"
  }
}
