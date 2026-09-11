"""The context object passed to a plugin's validate/render_result/get_url,
alongside `values`.

Generic information about the technical asset (and the user) a plugin call
is happening for. The exact list of fields belongs to ADR-0024, not the
deferred technical-asset-relationship ADR - only the richer data model
behind a technical asset's own record (tags, access modes, environment
configs, ...) is out of scope here.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from sdk.api_client.models import User


@dataclass
class PluginContext:
    technical_asset_id: Optional[UUID] = None
    technical_asset_name: Optional[str] = None
    output_port_id: Optional[UUID] = None
    data_product_id: Optional[UUID] = None
    domain: Optional[str] = None
    # Populated when the plugin declares `has_environments = True` (ADR-0024):
    # `environment` is the environment's name (e.g. "production"), reusing
    # the portal's existing `Environment` table; `environment_context` is
    # that row's own `context` field (e.g. an IAM role ARN template) with
    # `{{}}` substituted for the data product's `namespace` - the same
    # substitution a built-in type's own environment resolution already does
    # (see `app.core.aws.get_url._get_data_product_role_arn`).
    environment: Optional[str] = None
    environment_context: Optional[str] = None
    namespace: Optional[str] = None
    # The user on whose behalf this call happens. A plugin that needs to
    # fetch its own external credentials (e.g. an AWS STS AssumeRole, the
    # way the existing S3 plugin does via AuthService.get_aws_credentials)
    # does so scoped to this actor - the portal never holds long-lived
    # external secrets on a plugin's behalf.
    actor: Optional[User] = None
