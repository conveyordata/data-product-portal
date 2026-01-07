# ADR: Introduce Plugin-Based Architecture for Data Output Configuration

## Context and Problem Statement

The portal supports multiple data output integrations (e.g. S3, Snowflake, Databricks, Glue, Redshift). Each integration serves a common goal:

* Generate some kind of UI in the frontend where people can input technical fields
* Allow for infra provisioning
* Save configuration safely in the database
* Allow for access tiles in the frontend if needed

Previously, all data output configurations were hardcoded in the backend and frontend. There was no formal abstraction or extension mechanism. Adding or modifying an integration required touching multiple parts of the codebase and coordinating changes between backend and frontend. Small mistakes resulted in completely unavailable integrations.

This resulted in:

* Tight coupling between integrations
* Poor extensibility when introducing new integrations and lack of community-driven additions
* Lack of functionality on the infrastructure provisioning part

The system needs a more scalable and maintainable way to define data output configurations.

---

## Decision Drivers

* Reduce coupling and hardcoded logic
* Make adding new integrations simple and predictable
* Improve developer experience and maintainability
* Avoid YAML-based configuration with limited type safety
* Allow for extendable architecture to introduce infrastructure provisioning later on.

---

## Considered Options

* **Shared option: Python Plugin Architecture (Chosen)**
  Define each integration as a Python class using a shared base class.
  Frontend will be generated dynamically out of the provided fields (over REST API).
  Optional: Add auto-registering of new plugin technologies.

* **Option 1:** Strict columns and fields for configurations in database
  Current approach. Allows for easier migration of configurations because we know the content of the columns. Requires more dev-work and creation of migration script if extra columns are needed. Can introduce the risk of artificial (Wrong) mapping of certain technology columns onto our provided column names.

* **Option 2:** Free column choice, JSON blobs in database. Makes migrations almost impossible because JSON content is arbitrary. Makes mapping easier and does not require migration script creation at plugin creation.

---

## Decision Outcome

**Chosen option:** *Option: Python Plugin Architecture and Option 2: JSON Blobs*

We introduce a plugin-based architecture where each data output integration is defined as a self-contained Python class. These classes:

* Inherit from a common base (`DataOutputConfigurationPlugin`)
* Use Pydantic for schema validation
* Expose UI-relevant metadata
* Are automatically discovered and registered (Optional)
* Are exposed to the frontend via REST

This replaces the previously hardcoded approach and removes the need for YAML-based registries.
The JSON blob storage allows for extensible design without the limitation of our current column names.

### Confirmation

This decision is reflected in the application by:

* Migrating all existing integrations to class-based plugins
* Adding an auto-discovery registry (optional)
* Exposing integrations via the API
* Remove hardcoded frontend forms and introduce UI generation based on provided metadata

---

## Pros and Cons of the Options

### Option: Python Plugin Architecture

* **Good, because** it is type-safe, extensible, and keeps backend fields and UI configuration aligned
* **Good, because** in theory only 1 file needs to be changed to add a new integration
* **Bad, because** it requires clear conventions and discipline to avoid overly complex plugins

### Option 1:

* **Good, because** Migrations are relatively easy
* **Bad, because** If a developer wants other columns for their integrations a migration script is needed
* **Bad, because** Artificial (wrong) mappings might be introduced to make technologies work without a new migration

### Option 2:

* **Good, because** No migrations are needed for new integrations
* **Good, because** One-on-one mapping of technology terminology to database content.
* **Bad, because** Near impossible to do proper migrations of configurations later on.
