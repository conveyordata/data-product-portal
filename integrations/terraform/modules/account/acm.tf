resource "aws_acm_certificate" "auth" {
  domain_name       = "${var.hostname}.${var.hosted_zone}"
  validation_method = "DNS"

  tags = {
    Name = "${var.hostname}.${var.hosted_zone}"
  }

  lifecycle {
    create_before_destroy = true
  }
}

data "aws_route53_zone" "public_hosted_zone" {
  name         = var.hosted_zone
  private_zone = false
}

resource "aws_route53_record" "dns_validation" {
  for_each = {
    for dvo in aws_acm_certificate.auth.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value["name"]
  records         = [each.value["record"]]
  ttl             = 60
  type            = each.value["type"]
  zone_id         = data.aws_route53_zone.public_hosted_zone.id
}

resource "aws_acm_certificate_validation" "dns_validation" {
  certificate_arn         = aws_acm_certificate.auth.arn
  validation_record_fqdns = [for record in aws_route53_record.dns_validation : record.fqdn]
}
