// Create maps between public and private schemas
output "public_schemas" {
  value = { for k, v in databricks_schema.public_schemas : k => "${v.catalog_name}.${v.name}" }
}

output "private_schemas" {
  value = { for k, v in databricks_schema.private_schemas : k => "${v.catalog_name}.${v.name}" }
}

# output "public_tables" {
#   value = { for k, v in databricks_sql_table.public_tables: k => v.id }
# }

output "external_data_schemas" {
  value = { for k, v in databricks_schema.external_data_schema : k => "${v.catalog_name}.${v.name}" }
}

# output "external_locations" {
#   value = { for k, v in databricks_external_location.root_buckets : k => v.id }
# }

output "external_volumes" {
  value = { for k, v in databricks_volume.external_volumes : k => v.id }
}

output "external_schemas" {
  value = local.external_schemas
}

# output "data_products_with_external_outputs" {
#   value = local.data_products_with_external_outputs
# }

output "data_product_catalogs" {
  value = { for k, v in databricks_catalog.data_product_catalog : k => v.name }
}
