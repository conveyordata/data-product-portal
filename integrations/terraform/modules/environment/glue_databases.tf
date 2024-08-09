resource "aws_glue_catalog_database" "glue_database" {
  for_each = var.database_glossary

  name         = "${var.env}_${each.key}"
  location_uri = "s3://${aws_s3_bucket.datalake.id}/${each.value["s3"]}"
}
