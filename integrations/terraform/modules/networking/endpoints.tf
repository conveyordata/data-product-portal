module "interface_endpoints" {
  source   = "./interface_endpoints"
  for_each = var.create_vpc_endpoints == true ? local.interface_endpoints : toset([])

  service             = each.value
  prefix              = var.prefix
  aws_region          = var.aws_region
  vpc_id              = aws_vpc.vpc.id
  allowed_cidr_ranges = [var.vpc_cidr, var.vpc_secondary_cidr]
  subnet_ids          = local.non_routable_subnet_ids
}

data "aws_route_tables" "route_tables" {
  vpc_id = aws_vpc.vpc.id
}

resource "aws_vpc_endpoint" "s3" {
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"

  vpc_id          = aws_vpc.vpc.id
  route_table_ids = data.aws_route_tables.route_tables.ids
  policy          = var.enforce_endpoint_restrictions ? data.aws_iam_policy_document.s3_endpoint_policy.json : data.aws_iam_policy_document.s3_endpoint_policy_empty.json

  tags = {
    Name = "${var.prefix}-${local.aws_s3}-endpoint-${var.account_name}"
  }
}

data "aws_iam_policy_document" "s3_endpoint_policy_empty" {
  statement {
    effect    = "Allow"
    actions   = ["*"]
    resources = ["*"]
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
  }
}

data "aws_iam_policy_document" "s3_endpoint_policy" {
  # Allows Linux AMIs to update packages through the AWS package repositories
  statement {
    sid     = "AmazonManagedBucketAccess"
    effect  = "Allow"
    actions = ["s3:GetObject"]
    resources = [
      # Access required for Amazon ECR operations
      "arn:aws:s3:::prod-${var.aws_region}-starport-layer-bucket/*",
      # Access to allow connections to the Amazon API repositories
      # See https://aws.amazon.com/amazon-linux-ami/faqs/ (AMI v1)
      # See https://aws.amazon.com/premiumsupport/knowledge-center/ec2-al1-al2-update-yum-without-internet/ (AMI v1 and v2)
      "arn:aws:s3:::packages.${var.aws_region}.amazonaws.com/*",            #AMI v1
      "arn:aws:s3:::repo.${var.aws_region}.amazonaws.com/*",                #AMI v1
      "arn:aws:s3:::amazonlinux.${var.aws_region}.amazonaws.com/*",         #AMI v2
      "arn:aws:s3:::amazonlinux-2-repos-${var.aws_region}/*",               #AMI v2, yum sources.list file
      "arn:aws:s3:::amazonlinux-2-repos-${var.aws_region}.amazonaws.com/*", #AMI v2, actual packages
      # Access to AWS-managed transcribe location; AFAIK this is an undocumented location
      "arn:aws:s3:::aws-transcribe-${var.aws_region}-prod/${var.aws_account_id}/*",
      "arn:aws:s3:::al2023-repos-${var.aws_region}-de612dc2/*"
    ]

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
  }

  # Allow listing of buckets
  statement {
    # sid    = "DatalakeListBucketsPermissions"
    sid    = "FullAccessToAccountBucketsExtra"
    effect = "Allow"
    actions = [
      "s3:GetBucketLocation" # This operation does not set the s3:ResourceAccount, so I add it here so we get true s3:* permissions from the endpoint
    ]
    resources = ["arn:aws:s3:::*"]

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
  }

  # Allow generic S3 access (notably PUT) to specific buckets only
  # This prevents copying of data out from our data lake to external S3 buckets
  # (Note that tying this down )
  statement {
    sid       = "FullAccessToAccountBuckets"
    effect    = "Allow"
    actions   = ["s3:*"]
    resources = ["*"]
    condition {
      test     = "StringEquals"
      variable = "s3:ResourceAccount"
      values   = [var.aws_account_id]
    }
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
  }
}
