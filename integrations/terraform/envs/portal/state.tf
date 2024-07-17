terraform {
  backend "s3" {
    key = "terraform/cvr-pbac/infrastructure/state.tfstate"

    region         = "eu-west-1"
    bucket         = "cvr-pbac-s3-infrastructure-demo-jrivmq"
    kms_key_id     = "arn:aws:kms:eu-west-1:130966031144:key/41c40b50-cf9c-4afe-8333-37eacdfc9f54"
    encrypt        = true
    dynamodb_table = "terraform-state-locks-conveyor-demo"
  }
}
