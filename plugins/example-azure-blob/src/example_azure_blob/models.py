"""The plugin's own database table.

This is a standalone SQLAlchemy declarative base - it deliberately does NOT
import the portal's `app.database.database.Base`. The plugin owns this table
and its migrations completely; the portal only ever talks to it through the
plugin class, never through its own ORM relationships.
"""

import uuid

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

PluginBase = declarative_base()


class AzureBlobAsset(PluginBase):
    __tablename__ = "azure_blob_plugin_assets"

    # Not a locally generated id: the portal sets this to the same value as
    # the `data_outputs.id` row this asset belongs to (see app/plugins/router.py),
    # the same way the portal's own `configuration_id`-based plugins share a
    # primary key with `data_output_configurations`. No physical FK, since this
    # table lives in a separate migration history.
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    container_name = Column(String, nullable=False)
    path = Column(String, nullable=True)
    # Added in revision 0002 - present in the model from the start since the
    # model always describes the *current* shape; only the migration history
    # tells you how you got here.
    access_tier = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
