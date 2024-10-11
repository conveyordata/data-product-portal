resource "aws_glue_catalog_database" "glue_database" {
  for_each = local.create_glue_databases

  name         = each.value.database_name
  location_uri = each.value.database_uri
}
