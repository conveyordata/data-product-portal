resource "dataproductportal_data_product" "example" {
  name         = "Customer Analytics"
  description  = "Analytics data product for customer insights"
  about        = "Provides customer behavior and segmentation data."
  domain_id    = dataproductportal_domain.example.id
  type_id      = dataproductportal_data_product_type.example.id
  namespace    = "customer_analytics"
  lifecycle_id = "00000000-0000-0000-0000-000000000001"
  tag_ids      = [dataproductportal_tag.example.id]
  owners       = [data.dataproductportal_user.admin.id]
}
