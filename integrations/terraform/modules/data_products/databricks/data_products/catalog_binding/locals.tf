locals {
    environment_name_map = {
        "development" = "dev",
        "production"  = "prd"
    }
    // Only compute read-related variables if read_datasets is not empty
    has_read_datasets = length(try(var.data_product_config.read_datasets, [])) > 0

    read_datasets_items = local.has_read_datasets ? flatten([
        for dataset in var.data_product_config.read_datasets : var.datasets[dataset].data_outputs
    ]) : []
    read_data_products = distinct(local.has_read_datasets ? [
        for data_output in local.read_datasets_items : var.data_outputs[data_output].owner
    ] : [])

    read_catalogs = local.has_read_datasets ? [
        for data_product in local.read_data_products : var.managed_objects.data_product_catalogs[data_product]
    ]: []

    data_product_catalog = var.managed_objects.data_product_catalogs[var.data_product_name]
    data_product_workspace = var.workspaces_config["${var.business_unit}-${local.environment_name_map[var.environment]}"].id
}
