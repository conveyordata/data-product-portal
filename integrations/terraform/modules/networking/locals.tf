locals {
  routable_subnet_ids     = [for k, v in aws_subnet.routable_subnets : v.id]
  non_routable_subnet_ids = [for k, v in aws_subnet.non_routable_subnets : v.id]
  #route_table_ids         = [for v in data.aws_route_tables.route_tables : v.id]

  interface_endpoints = toset([
    "athena",
    "autoscaling",
    "ec2",
    "ec2messages",
    "glue",
    "lambda",
    "monitoring",
    "ssm",
    "ssmmessages",
    "sts",
    "ecr.dkr",
    "ecr.api",
    "elasticloadbalancing",
    "sqs",
    "aps-workspaces",
    "aps",
    "kms",
    "rds",
    "logs",
    "fsx",
    "ds" # (active) directory services
  ])
}
