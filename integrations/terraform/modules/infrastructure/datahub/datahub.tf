locals {
  #ecr_repository                = "${var.aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${var.prefix}-${local.aws_ecr_dkr}-${var.project_name}"
  ecr_repo = "130966031144.dkr.ecr.eu-west-1.amazonaws.com"

  datahub_helm_chart_version = "0.2.186"

  subnet_ids_str = join(",", [for k, v in var.vpc_config.routable_subnets : v.subnet_id])

  host = "datahub.${var.account_config.hosted_zone}"
  #host = "${var.hostname}.${var.hosted_zone}"

  datahub_values = <<EOF
datahub-gms:
  enabled: true
  service:
    type: ClusterIP

datahub-frontend:
  service:
    type: NodePort
  enabled: true
  ingress:
    enabled: true
    annotations:
      kubernetes.io/ingress.class: alb
      alb.ingress.kubernetes.io/scheme: internet-facing
      alb.ingress.kubernetes.io/target-type: instance
      alb.ingress.kubernetes.io/certificate-arn: ${var.account_config.certificate_arn}
      alb.ingress.kubernetes.io/subnets: ${local.subnet_ids_str}
      alb.ingress.kubernetes.io/inbound-cidrs: 0.0.0.0/0
      alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS":443}]'
      alb.ingress.kubernetes.io/actions.ssl-redirect: '{"Type": "redirect", "RedirectConfig": { "Protocol": "HTTPS", "Port": "443", "StatusCode": "HTTP_301"}}'
    hosts:
      - paths:
        - /*
        host: ${local.host}
        redirectPaths:
          - path: /*
            name: ssl-redirect
            port: use-annotation

  # Temporary workaround to change the default password of Datahub
  # Secret created manually by running: kubectl -n datahub create secret generic datahub-pass-secret --from-literal=token=datahub:<your_pass>
  extraVolumes:
    - name: user-props
      secret:
        secretName: datahub-pass-secret
  extraVolumeMounts:
      - name: user-props
        mountPath: /datahub-frontend/conf/user.props
        subPath: token
        readOnly: true

datahubSystemUpdate:
  enabled: false

acryl-datahub-actions:
  enabled: false

global:
  datahub:
    metadata_service_authentication:
      enabled: true
EOF
}


resource "kubernetes_namespace" "datahub_namespace" {
  metadata {
    name = "datahub"
  }
}

resource "kubernetes_secret" "datahub_mysql-secrets" {
  metadata {
    name      = "mysql-secrets"
    namespace = kubernetes_namespace.datahub_namespace.metadata[0].name
  }
  data = {
    mysql-root-password = "datahub"
  }
}

resource "kubernetes_secret" "datahub_neo4j-secrets" {
  metadata {
    name      = "neo4j-secrets"
    namespace = kubernetes_namespace.datahub_namespace.metadata[0].name
  }
  data = {
    neo4j-password = "datahub"
  }
}

resource "helm_release" "prerequisites" {
  name       = "prerequisites"
  repository = "https://helm.datahubproject.io/"
  chart      = "datahub-prerequisites"
  namespace  = kubernetes_namespace.datahub_namespace.metadata[0].name

  set {
    name  = "neo4j.enabled"
    value = false
  }

  set {
    name  = "elasticsearch.resources.limits.memory"
    value = "2000M"
  }

}

resource "helm_release" "datahub" {
  name       = "datahub"
  wait       = false
  repository = "https://helm.datahubproject.io/"
  chart      = "datahub"
  version    = local.datahub_helm_chart_version
  namespace  = kubernetes_namespace.datahub_namespace.metadata[0].name
  values     = [local.datahub_values]
  timeout    = 600
  depends_on = [helm_release.prerequisites]
}
