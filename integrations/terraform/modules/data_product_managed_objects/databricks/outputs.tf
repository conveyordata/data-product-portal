output "data_product_catalogs" {
  value = { for data_product, catalog in databricks_catalog.data_product_catalog : data_product => catalog.name }
}

output "public_schemas" {
  value = { for data_product, schema in databricks_schema.public_schemas : data_product => "${schema.catalog_name}.${schema.name}" }
}

output "private_schemas" {
  value = { for data_product, schema in databricks_schema.private_schemas : data_product => "${schema.catalog_name}.${schema.name}" }
}

output "external_data_schemas" {
  value = { for data_product, schema in databricks_schema.external_data_schema : data_product => "${schema.catalog_name}.${schema.name}" }
}

output "external_volumes" {
  value = { for data_output, volume in databricks_volume.external_volumes : data_output => volume.id }
}
