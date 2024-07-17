locals {
  # Retrieve all write data_ids
  write_data_ids = [for data_id, v in var.data_ids : data_id if contains(v.owner, var.project_name)]

  # Retrieve all read data_ids. You can also read what you can write
  read_data_ids = concat(flatten([
    for data_topic in var.project_config.read_data_topics : var.data_topics[data_topic]["data_ids"]]
  ), local.write_data_ids)

  # Retrieve all S3 paths for the S3 write data ids
  write_s3_paths = [
    for s3 in flatten([for data_id in local.write_data_ids : var.data_ids[data_id].s3]) :
    "${var.environment_config[s3["bucket_name"]]["bucket_arn"]}${s3["path"]}"
  ]

  write_s3_buckets = [
    for s3 in flatten([for data_id in local.write_data_ids : var.data_ids[data_id].s3]) :
    var.environment_config[s3["bucket_name"]]["bucket_arn"]
  ]

  # Retrieve all S3 paths for the S3 read data_ids
  read_s3_paths = [
    for s3 in flatten([for data_id in local.read_data_ids : var.data_ids[data_id].s3]) :
    "${var.environment_config[s3["bucket_name"]]["bucket_arn"]}${s3["path"]}"
  ]

  read_s3_buckets = [
    for s3 in flatten([for data_id in local.read_data_ids : var.data_ids[data_id].s3]) :
    var.environment_config[s3["bucket_name"]]["bucket_arn"]
  ]

  # Retrieve all S3 paths for the Glue write data_ids
  write_glue_paths = [
    for glue in flatten([for data_id in local.write_data_ids : var.data_ids[data_id].glue]) :
    "${var.environment_config["datalake"]["bucket_arn"]}/${var.environment_config.database_glossary[split("/", glue)[0]]["s3"]}/${split("/", glue)[1]}"
  ]

  write_glue_buckets = [
    for glue in flatten([for data_id in local.write_data_ids : var.data_ids[data_id].glue]) :
    var.environment_config["datalake"]["bucket_arn"]
  ]

  write_glue_databases = distinct([
    for glue in flatten([for data_id in local.write_data_ids : var.data_ids[data_id].glue]) :
    var.environment_config.database_glossary[split("/", glue)[0]]["glue_database"]
  ])

  write_glue_tables = [
    for glue in flatten([for data_id in local.write_data_ids : var.data_ids[data_id].glue]) :
    "${var.environment_config.database_glossary[split("/", glue)[0]]["glue_database"]}/${split("/", glue)[1]}"
  ]

  # Retrieve all S3 paths for the Glue read data_ids
  read_glue_paths = [
    for glue in flatten([for data_id in local.read_data_ids : var.data_ids[data_id].glue]) :
    "${var.environment_config["datalake"]["bucket_arn"]}/${var.environment_config.database_glossary[split("/", glue)[0]]["s3"]}/${split("/", glue)[1]}"
  ]

  read_glue_buckets = [
    for glue in flatten([for data_id in local.read_data_ids : var.data_ids[data_id].glue]) :
    var.environment_config["datalake"]["bucket_arn"]
  ]

  # Add datalake explicitly as we always grant it default /project access
  bucket_list = distinct(concat(local.write_s3_buckets, local.write_s3_buckets, local.write_glue_buckets, local.read_glue_buckets, [var.environment_config["datalake"]["bucket_arn"]]))

  # Combine all paths together
  read_paths = flatten([for k in distinct(concat(
    # Also add dedicated project folder in there
    local.read_s3_paths, local.read_glue_paths, ["${var.environment_config["datalake"]["bucket_arn"]}/${var.project_folder_prefix}/${var.project_name}"]
  )) : [k, "${k}/*"]])

  read_paths_chunk_list = chunklist(local.read_paths, var.read_chunk_size)

  write_paths = flatten([for k in distinct(concat(
    # Also add dedicated project folder in there
    local.write_s3_paths, local.write_glue_paths, ["${var.environment_config["datalake"]["bucket_arn"]}/${var.project_folder_prefix}/${var.project_name}"]
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
    for s3 in flatten([for data_id in local.read_data_ids : var.data_ids[data_id].s3]) :
    var.environment_config[s3["bucket_name"]]["kms_key_arn"]
    ], [
    var.environment_config["datalake"]["kms_key_arn"]
  ]))

  # Write KMS keys
  write_kms_keys = distinct(concat([
    for s3 in flatten([for data_id in local.write_data_ids : var.data_ids[data_id].s3]) :
    var.environment_config[s3["bucket_name"]]["kms_key_arn"]
    ], [
    var.environment_config["datalake"]["kms_key_arn"]
  ]))
}
