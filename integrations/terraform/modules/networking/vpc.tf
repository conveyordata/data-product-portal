resource "aws_vpc" "vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.prefix}-${local.aws_vpc}-${var.vpc_name}-${var.account_name}"
  }
}

resource "aws_vpc_ipv4_cidr_block_association" "secondary_cidr" {
  vpc_id     = aws_vpc.vpc.id
  cidr_block = var.vpc_secondary_cidr
}

resource "aws_subnet" "routable_subnets" {
  for_each = var.routable_subnets

  vpc_id            = aws_vpc.vpc.id
  cidr_block        = each.value.cidr
  availability_zone = each.value.az

  tags = {
    Name = "${var.prefix}-${local.aws_vpc}-${var.vpc_name}-routable-${each.key}-${var.account_name}"
    # Make sure that these subnets are used to set automatically load balancers
    "kubernetes.io/role/elb" = 1
  }
}

resource "aws_nat_gateway" "nat_gateway" {
  for_each = aws_subnet.routable_subnets

  subnet_id         = each.value.id
  connectivity_type = "private"
}

resource "aws_subnet" "non_routable_subnets" {
  for_each = var.non_routable_subnets

  vpc_id            = aws_vpc_ipv4_cidr_block_association.secondary_cidr.vpc_id
  cidr_block        = each.value.cidr
  availability_zone = each.value.az

  tags = {
    Name = "${var.prefix}-${local.aws_vpc}-${var.vpc_name}-nonroutable-${each.key}-${var.account_name}"
  }
}

# Create specific route table for the non-routable subnet
resource "aws_route_table" "route_table" {
  for_each = aws_subnet.routable_subnets

  vpc_id = aws_vpc.vpc.id
  tags = {
    Name = "${var.prefix}-${local.aws_vpc}-${var.vpc_name}-nonroutable-route-table-${each.key}-${var.account_name}"
  }
}

resource "aws_route" "nat_route" {
  for_each = aws_route_table.route_table

  route_table_id = each.value.id
  # all non local traffic needs to be routed to the nat gateway
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.nat_gateway[each.key].id
}

# Associate the route table to the local subnet
resource "aws_route_table_association" "route_table_association" {
  for_each = aws_subnet.non_routable_subnets

  subnet_id      = each.value.id
  route_table_id = aws_route_table.route_table[each.key].id
}
