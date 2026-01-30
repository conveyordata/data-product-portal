# S3 Data Output Plugin

This is an external plugin for the Data Product Portal that provides S3 bucket output configuration.

## Installation

From the plugin directory:

```bash
pip install -e .
```

Or to install from a built package:

```bash
pip install data-product-portal-s3-plugin
```

## How It Works

This plugin is automatically discovered by the Data Product Portal through Python entry points. When the portal starts, it:

1. Scans for packages that register the `data_product_portal.plugins` entry point
2. Loads the plugin class (`S3DataOutput`)
3. Registers it in the plugin registry
4. Makes it available through the `/api/v2/plugins/` REST API

## Development

To develop this plugin:

1. Install the Data Product Portal backend in development mode
2. Install this plugin in editable mode: `pip install -e .`
3. The plugin will be available when you start the portal

## Plugin Structure

- `schema.py` - Pydantic schema for validation and UI generation
- `model.py` - SQLAlchemy model for database persistence
- `setup.py` - Package configuration with entry point registration

## Migration

The plugin includes a migration file path that points to:
`app/database/alembic/versions/2026_01_28_1243-s3_separate_table.py`

This migration creates the `s3_data_output_configurations` table.
