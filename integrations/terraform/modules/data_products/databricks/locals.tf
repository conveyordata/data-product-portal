locals {
  # Filter data products and outputs for the business unit
  current_purpose_data_products = { for k, v in var.data_product_glossary : k => v if v.business_unit == var.business_unit }
  current_purpose_data_outputs = { for k, v in var.data_outputs : k => v if var.data_product_glossary[v.owner].business_unit == var.business_unit }
}
