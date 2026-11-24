# Scope technical asset namespace uniqueness per Data Product and Technical Asset Type

## Context and Problem Statement

Every Technical Asset has a namespace. It is generated from the asset name (or typed in by the creator), must match `[a-z0-9+=,.@_-]` with at most 64 characters, and can not be changed after creation.

Until now the namespace had to be unique within the owning Data Product. A Data Product with an S3 Technical Asset and an SSM Parameter Store Technical Asset for the same dataset could therefore not call both `orders`, even though they are different kinds of resources.

The technical asset namespace does not drive any physical naming. Plugins build and validate physical identifiers (databases, catalogs, buckets, suffixes) from the Data Product namespace, and no plugin, route or backend provisioner looks up a Technical Asset by its namespace. The one consumer that did is the legacy Terraform exporter (`integrations/terraform/envs/portal/read_portal_config.py`): it keyed exported assets, and the Output Port references to them, by `data product namespace / asset namespace`, so two assets sharing that pair would silently collapse into one.

Which scope should technical asset namespace uniqueness have?

## Decision Drivers

* Users want the same name for assets of different Technical Asset Types that belong together (e.g. an S3 path and the SSM parameter describing it).
* The namespace must stay a reliable identifier for anything that refers to Technical Assets by name, such as integrations or lineage.
* Global uniqueness of physical resources is the job of the plugin configuration validation, not of the asset namespace.
* The change should not require a data migration.

## Considered Options

* **Option 1: Unique per Data Product** Keep the current rule.
* **Option 2: Unique per Data Product and Technical Asset Type** Two assets in the same Data Product may share a namespace when their Technical Asset Type differs.
* **Option 3: Unique across the portal** Every technical asset namespace is unique across all Data Products.
* **Option 4: No uniqueness** Treat the namespace as a free label.

## Decision Outcome

**Chosen option:** *Option 2: Unique per Data Product and Technical Asset Type*. It allows the requested naming, keeps a stable composite key (`data product namespace / Technical Asset Type / asset namespace`), and needs no migration because every existing namespace is already unique per Data Product.

### Confirmation

* A Technical Asset Type is the name of a plugin with its own configuration (e.g. `S3TechnicalAssetConfiguration`), stored on the configuration as `configuration_type`. The backend encodes it as the `TechnicalAssetType` type, which rejects names that are not an installed Technical Asset Type.
* `TechnicalAssetService.validate_namespace` checks uniqueness on owner, namespace and Technical Asset Type. Creating a Technical Asset and the validation endpoint both use it.
* `GET /api/v2/resource_names/validate` with `model=technical_asset` requires `data_product_id` and `technical_asset_type`. It returns 400 when either is missing and 422 for an unknown Technical Asset Type. This is a breaking change for API clients that called it without a type.
* The Technical Asset form checks the namespace once a Technical Asset Type is selected, and checks it again when the type changes.
* Uniqueness is enforced in the application only; there is no database constraint.
* The Terraform exporter keys assets by `data product namespace / asset namespace / asset id`, in both `data_outputs.yaml` and the Output Port references in `datasets.yaml`. The keys are only map lookups, not Terraform resource addresses, so no state moves. Both files must be regenerated together; a mix of old and new files breaks the references. The exporter still calls the removed pre-v2 routes; its migration to the v2 API is a separate change and must keep this key.

## Pros and Cons of the Options

### Option 1: Unique per Data Product

* **Good, because** `data product / asset namespace` identifies exactly one asset.
* **Bad, because** assets of different Technical Asset Types that belong together can not share a name, without any technical reason.

### Option 2: Unique per Data Product and Technical Asset Type

* **Good, because** related assets of different Technical Asset Types can share a namespace.
* **Good, because** existing data stays valid, no migration is needed.
* **Neutral, because** the identifying key now includes the Technical Asset Type; consumers that referred to assets by `data product / namespace` alone must add the type.
* **Bad, because** the validation endpoint needs the Technical Asset Type, which breaks clients that omitted it.

### Option 3: Unique across the portal

* **Good, because** the namespace alone identifies an asset.
* **Bad, because** teams must invent prefixes for common names like `orders`, while the physical names are already scoped by the Data Product namespace.
* **Bad, because** existing duplicates across Data Products would need a migration.

### Option 4: No uniqueness

* **Good, because** it is the simplest rule.
* **Bad, because** the namespace no longer identifies anything, and two assets of the same Technical Asset Type could not be told apart by name.
