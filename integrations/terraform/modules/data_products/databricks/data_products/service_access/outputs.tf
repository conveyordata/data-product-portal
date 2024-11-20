output "service_access_group" {
    value = databricks_group.service_access_group.id
}

output "service_access_group_acl_principal_id" {
    value = databricks_group.service_access_group.acl_principal_id
}
