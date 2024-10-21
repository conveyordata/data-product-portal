terraform {
  backend "s3" {
    # Path where terraform state file will to be stored
    key = "terraform/portal/infrastructure/state.tfstate"

    # AWS region of the S3 bucket
    region = "eu-west-1"
    # Name of the bucket where the terraform state will be stored in
    bucket = "data-product-portal-infrastructure-kjsdfc/"
    # KMS key arn for the S3 bucket key to encrypt the terraform state with
    kms_key_id = "arn:aws:kms:eu-west-1:130966031144:key/xxxxxxxx"
    # Whether the terraform state needs to be encrypted, say yes here ;)
    encrypt = true
    # Dynamo table to store terraform state locks
    dynamodb_table = "terraform-state-locks-portal"
  }
}
