resource "dataproductportal_output_port" "example" {
  data_product_id = dataproductportal_data_product.example.id
  name            = "Customer Segments"
  namespace       = "customer_segments"
  description     = "Output port for customer segmentation data"
  access_type     = "internal"
  tag_ids         = [dataproductportal_tag.example.id]
  owners          = [data.dataproductportal_user.admin.id]
}
