locals {
  # Extract glossaries
  bucket_glossary   = var.environment_config.bucket_glossary
  database_glossary = var.managed_objects.database_glossary
  # Default datalake bucket
  default_bucket = [for bucket_id, bucket in local.bucket_glossary : bucket if bucket.is_default][0]

  # Retrieve all write data_ids
  write_data_outputs = [for data_id, v in var.data_outputs : data_id if v.owner == var.data_product_name]

  # Retrieve all read data_ids. You can also read what you can write
  read_data_outputs = concat(flatten([
    for dataset in var.data_product_config.read_datasets : var.datasets[dataset].data_outputs]
  ), local.write_data_outputs)

  # Retrieve all S3 paths for the S3 write data ids
  write_s3_paths = [
    for s3 in flatten([for data_id in local.write_data_outputs : var.data_outputs[data_id].s3]) :
    s3.path == "" ?
    "${local.bucket_glossary[s3.bucket_identifier].bucket_arn}${s3.suffix}" :
    "${local.bucket_glossary[s3.bucket_identifier].bucket_arn}${s3.suffix}/${s3.path}"
  ]

  write_s3_buckets = [
    for s3 in flatten([for data_id in local.write_data_outputs : var.data_outputs[data_id].s3]) :
    local.bucket_glossary[s3.bucket_identifier].bucket_arn
  ]

  # Retrieve all S3 paths for the S3 read data_ids
  read_s3_paths = [
    for s3 in flatten([for data_id in local.read_data_outputs : var.data_outputs[data_id].s3]) :
    s3.path == "" ?
    "${local.bucket_glossary[s3.bucket_identifier].bucket_arn}${s3.suffix}" :
    "${local.bucket_glossary[s3.bucket_identifier].bucket_arn}${s3.suffix}/${s3.path}"
  ]

  read_s3_buckets = [
    for s3 in flatten([for data_id in local.read_data_outputs : var.data_outputs[data_id].s3]) :
    local.bucket_glossary[s3.bucket_identifier].bucket_arn
  ]

  # Retrieve all S3 paths for the Glue write data_ids
  write_glue_paths = flatten([
    for glue in flatten([for data_id in local.write_data_outputs : var.data_outputs[data_id].glue]) :
    glue.table_path == "" ?
    "${local.bucket_glossary[glue.bucket_identifier].bucket_arn}/${glue.database_path}" :
    "${local.bucket_glossary[glue.bucket_identifier].bucket_arn}/${glue.database_path}/${glue.table_path}"
  ])

  write_glue_buckets = [
    for glue in flatten([for data_id in local.write_data_outputs : var.data_outputs[data_id].glue]) :
    local.bucket_glossary[glue.bucket_identifier].bucket_arn
  ]

  write_glue_databases = distinct([
    for glue in flatten([for data_id in local.write_data_outputs : var.data_outputs[data_id].glue]) :
    local.database_glossary[glue.database][glue.suffix]
  ])

  write_glue_tables = flatten([
    for glue in flatten([for data_id in local.write_data_outputs : var.data_outputs[data_id].glue]) :
    "${local.database_glossary[glue.database][glue.suffix]}/${glue.table}"
  ])

  # Retrieve all S3 paths for the Glue read data_ids
  read_glue_paths = flatten([
    for glue in flatten([for data_id in local.read_data_outputs : var.data_outputs[data_id].glue]) :
    glue.table_path == "" ?
    "${local.bucket_glossary[glue.bucket_identifier].bucket_arn}/${glue.database_path}" :
    "${local.bucket_glossary[glue.bucket_identifier].bucket_arn}/${glue.database_path}/${glue.table_path}"
  ])

  read_glue_buckets = [
    for glue in flatten([for data_id in local.read_data_outputs : var.data_outputs[data_id].glue]) :
    local.bucket_glossary[glue.bucket_identifier].bucket_arn
  ]

  # Add default bucket explicitly as we always grant it default /project access
  bucket_list = distinct(concat(local.write_s3_buckets, local.read_s3_buckets, local.write_glue_buckets, local.read_glue_buckets, [local.default_bucket.bucket_arn]))

  # Combine all paths together
  dedicated_project_folder_path = "${local.default_bucket.bucket_arn}/${var.data_product_folder_prefix}/${var.data_product_name}"

  read_paths = flatten([for k in distinct(concat(
    # Also add dedicated project folder in there
    local.read_s3_paths, local.read_glue_paths, [local.dedicated_project_folder_path]
  )) : [k, "${k}/*"]])

  read_paths_chunk_list = chunklist(local.read_paths, var.read_chunk_size)

  write_paths = flatten([for k in distinct(concat(
    # Also add dedicated project folder in there
    local.write_s3_paths, local.write_glue_paths, [local.dedicated_project_folder_path]
  )) : [k, "${k}/*"]])

  write_paths_chunk_list = chunklist(local.write_paths, var.write_chunk_size)

  # Chunk them to allow for a lot of different paths
  chunked_read_paths = {
    for idx, chunk in local.read_paths_chunk_list : "Part${idx}" => chunk
  }

  chunked_write_paths = {
    for idx, chunk in local.write_paths_chunk_list : "Part${idx}" => chunk
  }

  # Read KMS keys
  read_kms_keys = distinct(concat([
    for s3 in flatten([for data_id in local.read_data_outputs : var.data_outputs[data_id].s3]) :
    local.bucket_glossary[s3.bucket_identifier].kms_key_arn
    ], [
    for glue in flatten([for data_id in local.read_data_outputs : var.data_outputs[data_id].glue]) :
    local.bucket_glossary[glue.bucket_identifier].kms_key_arn
    ], [
    local.default_bucket.kms_key_arn
  ]))

  # Write KMS keys
  write_kms_keys = distinct(concat([
    for s3 in flatten([for data_id in local.write_data_outputs : var.data_outputs[data_id].s3]) :
    local.bucket_glossary[s3.bucket_identifier].kms_key_arn
    ], [
    for glue in flatten([for data_id in local.write_data_outputs : var.data_outputs[data_id].glue]) :
    local.bucket_glossary[glue.bucket_identifier].kms_key_arn
    ], [
    local.default_bucket.kms_key_arn
  ]))
}
