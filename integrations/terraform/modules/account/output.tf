output "certificate_arn" {
  value = aws_acm_certificate.auth.arn
}

output "hosted_zone" {
  value = var.hosted_zone
}

output "hosted_zone_arn" {
  value = var.hosted_zone_arn
}

output "hostname" {
  value = var.hostname
}
