# This daemonset will allow all nodes to install the SSM agent on startup
resource "kubernetes_daemonset" "ssm_daemonset" {
  metadata {
    name = "ssm-installer"
    labels = {
      k8s-app = "ssm-installer"
    }
    namespace = "kube-system"
  }
  spec {
    selector {
      match_labels = {
        k8s-app = "ssm-installer"
      }
    }
    template {
      metadata {
        labels = {
          k8s-app = "ssm-installer"
        }
      }
      spec {
        container {
          name    = "sleeper"
          image   = "public.ecr.aws/docker/library/busybox"
          command = ["sh", "-c", "echo I keep things running! && sleep 3600"]
        }
        init_container {
          image             = "public.ecr.aws/amazonlinux/amazonlinux"
          image_pull_policy = "Always"
          name              = "ssm"
          command           = ["/bin/bash"]
          args              = ["-c", "echo '* * * * * root yum install -y https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_amd64/amazon-ssm-agent.rpm & rm -rf /etc/cron.d/ssmstart' > /etc/cron.d/ssmstart"]
          security_context {
            allow_privilege_escalation = true
          }
          volume_mount {
            mount_path = "/etc/cron.d"
            name       = "cronfile"
          }
          termination_message_policy = "File"
          termination_message_path   = "/dev/termination-log"
        }
        volume {
          name = "cronfile"
          host_path {
            path = "/etc/cron.d"
            type = "Directory"
          }
        }
        dns_policy                       = "ClusterFirst"
        restart_policy                   = "Always"
        scheduler_name                   = "default-scheduler"
        termination_grace_period_seconds = 30
      }
    }
  }
}
