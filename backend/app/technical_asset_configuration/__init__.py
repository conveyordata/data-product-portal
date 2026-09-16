# Plugin classes are registered by importing them, which
# app/technical_asset_configuration/schema_union.py does. Keeping this module
# empty means importing base_schema (which every plugin does) stays cheap and
# free of import cycles.
