output "vpc_id" {
  value = aws_vpc.vpc.id
}

output "vpc_cidr_block" {
  value = aws_vpc.vpc.cidr_block
}

output "vpc_secondary_cidr_block" {
  value = aws_vpc_ipv4_cidr_block_association.secondary_cidr.cidr_block
}

output "s3_endpoint_id" {
  value = aws_vpc_endpoint.s3.id
}

output "routable_subnets" {
  value = {
    for k, v in aws_subnet.routable_subnets : k => {
      subnet_id         = v.id
      subnet_cidr_block = v.cidr_block
      az                = v.availability_zone
    }
  }
}

output "non_routable_subnets" {
  value = {
    for k, v in aws_subnet.non_routable_subnets : k => {
      subnet_id         = v.id
      subnet_cidr_block = v.cidr_block
      az                = v.availability_zone
    }
  }
}

output "route_table_ids" {
  value = data.aws_route_tables.route_tables.ids
}
