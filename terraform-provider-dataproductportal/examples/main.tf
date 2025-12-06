terraform {
  required_providers {
    dataproductportal = {
      source = "registry.terraform.io/data-product-portal/dataproductportal"
    }
  }
}

provider "dataproductportal" {
  base_url = "https://api.example.com"
  api_key  = var.api_key
}

variable "api_key" {
  type      = string
  sensitive = true
}

# Environments
resource "dataproductportal_environment" "dev" {
  name = "Development"
}

resource "dataproductportal_environment" "prod" {
  name = "Production"
}

# Platforms
resource "dataproductportal_platform" "aws" {
  name = "AWS"
}

# Tags
resource "dataproductportal_tag" "pii" {
  name = "PII"
}

resource "dataproductportal_tag" "financial" {
  name = "Financial"
}

# Domains
resource "dataproductportal_domain" "analytics" {
  name        = "Analytics"
  description = "Analytics domain for all reporting data products"
}

resource "dataproductportal_domain" "marketing" {
  name        = "Marketing"
  description = "Marketing domain"
}

# Data Product Types
resource "dataproductportal_data_product_type" "batch" {
  name     = "Batch"
  icon_key = "batch"
}

resource "dataproductportal_data_product_type" "streaming" {
  name     = "Streaming"
  icon_key = "streaming"
}

# Data Products
resource "dataproductportal_data_product" "customer_analytics" {
  name        = "Customer Analytics"
  description = "Customer behavior analytics data product"
  domain_id   = dataproductportal_domain.analytics.id
  type_id     = dataproductportal_data_product_type.batch.id
}

# Datasets
resource "dataproductportal_dataset" "customer_events" {
  name        = "Customer Events"
  description = "Raw customer event data"
  domain_id   = dataproductportal_domain.analytics.id
}

# Data Outputs
resource "dataproductportal_data_output" "customer_s3" {
  name        = "Customer S3 Export"
  description = "S3 export of customer data"
  owner_id    = dataproductportal_data_product.customer_analytics.id
  configuration = jsonencode({
    type   = "s3"
    bucket = "customer-data-bucket"
    prefix = "exports/"
  })
}

# Role Assignments (example - assign admin role to user)
# resource "dataproductportal_role_assignment" "admin" {
#   user_id = "user-uuid"
#   role_id = "admin-role-uuid"
#   scope   = "global"
# }

# Data Sources
data "dataproductportal_domain" "analytics" {
  id = dataproductportal_domain.analytics.id
}

output "domain_name" {
  value = data.dataproductportal_domain.analytics.name
}
