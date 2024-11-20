locals {
  aws_vpc            = "vpc"
  aws_ec2            = "ec2"
  aws_ecr_api        = "ecr-api"
  aws_ecr_dkr        = "ecr-dkr"
  aws_iam            = "iam"
  aws_security_group = "sg"
  aws_s3             = "s3"
  aws_kms            = "kms"
  aws_glue           = "glue"
  aws_sns            = "sns"
  aws_redshift       = "rsh"
  aws_secret_manager = "scr"
  aws_eks            = "eks"

  aws_actions = {
    s3 = {
      readwrite = [
        "s3:*Object", # create, upload, list, complete and abort multipart uploads / parts
      ]
      writeonly = [
        "s3:List*",
        # list objects, object versions, parts
        "s3:PutObject",
        "s3:DeleteObject",
      ],
      readonly = [
        "s3:List*",
        "s3:Get*",
      ]
    },
    kms = {
      readwrite = [
        "kms:Decrypt",
        "kms:Encrypt",
        "kms:GenerateDataKey*",
        "kms:ReEncrypt*",
        "kms:DescribeKey",
      ],
      # WARNING: writeonly does not give decrypt permission, which will make it impossible to use multipart uploads.
      # Consider using readwrite KMS permissions even when giving only writeonly S3 permissions.
      # See: https://aws.amazon.com/premiumsupport/knowledge-center/s3-large-file-encryption-kms-key/
      writeonly = [
        "kms:Encrypt",
        "kms:GenerateDataKey*",
        "kms:ReEncrypt*",
        "kms:DescribeKey",
      ],
      readonly = [
        "kms:Decrypt",
        "kms:DescribeKey",
      ]
    }
  }
}
