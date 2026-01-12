# ADR: Introduce Plugin-Based Architecture for Data Output Configuration

## Context and Problem Statement

The portal supports multiple data output integrations (e.g. S3, Snowflake, Databricks, Glue, Redshift). Each integration serves a common goal:

* Generate UI in the frontend where users can input technical fields
* Allow for infrastructure provisioning
* Persist configuration safely in the database
* Allow for access tiles in the frontend if needed

Previously, all data output configurations were hardcoded in both backend and frontend. There was no formal abstraction or extension mechanism. Adding or modifying an integration required touching multiple parts of the codebase and coordinating backend and frontend changes. Small mistakes resulted in unavailable or broken integrations.

This resulted in:

* Tight coupling between integrations
* Poor extensibility and no realistic path for community or external contributions
* No clear ownership or extension point for infrastructure provisioning logic

The system needs a more scalable and maintainable way to define data output configurations as a stepping stone toward a real plugin system, without requiring another major refactor later.

---

## Decision Drivers

* Reduce coupling and hardcoded logic
* Make adding new integrations simple and predictable
* Improve developer experience and maintainability
* Avoid YAML-based configuration with limited type safety
* Prepare the codebase for future extensibility without committing to a full plugin runtime yet
* Align with a longer-term vision where integrations can be developed and deployed independently

---

## Considered Options

* **Shared option: Python Plugin Architecture (Chosen)**
  Define each integration as a Python class using a shared base class.
  Frontend configuration is generated dynamically over REST.
  Plugins are discovered through code-level registration.

* **Option 1:** Strict columns and fields for configurations in the database, single table.
  Current approach. Easier migrations but requires schema changes for every new integration. Encourages artificial mappings between technologies and database columns.

* **Option 2:** Free column choice using JSON blobs
  Store configuration as JSON per integration. Avoids migrations when adding integrations but complicates long-term data evolution.

* **Option 3:** Strict columns and fields for configurations in the database, table per plugin.
  Each plugin has their own table, with strict column mappings.

### Second discussion: Plugin provisioning

* **Option 1:** Plugins are an internal extension mechanism only
  Integrations live in the portal codebase and require a rebuild to be added.

* **Option 2:** Plugins can be delivered independently
  Integrations can be installed or mounted without rebuilding the core portal image. Restart might be needed.

---

## Decision Outcome

**Chosen option:**
*Python Plugin Architecture* combined with *Option 3: Table per plugin*

We introduce a plugin-based architecture where each data output integration is defined as a self-contained Python class. These classes:

* Inherit from a common base (`AssetProviderPlugin`)
* Use Pydantic for schema validation
* Expose UI-relevant metadata
* Are discovered via a registry at application startup
* Are exposed to the frontend via REST endpoints
* Manage their own database migration and creation of columns.

This replaces the previously hardcoded approach and removes YAML-based registries.
Having a table schema per plugin allows each integration to map its terminology one-to-one to the database and allows for easier migrations down the line.

### Plugin provisioning decision

For now:
* Plugins are Python packages installed into the portal environment
* Adding a plugin requires:

  * Installing the package (e.g. `pip install`)
  * Restarting the portal
* No hot-loading at runtime is required
* No external execution or sandboxing is introduced
* It is sufficient to provide the list of configured plugins via e.g. an environment variable.

This aligns with existing Python ecosystems (e.g. Airflow plugins) and avoids premature complexity, while still enabling future evolution.

---

## Confirmation

This decision is reflected in the application by:

* Migrating all existing integrations to class-based plugins
* Discover new plugins at startup (environment variable is sufficient for discovery)
* Exposing integration metadata via REST APIs
* Replacing hardcoded frontend forms with dynamically generated UI
* Persisting configuration as JSON blobs scoped to the plugin type

---

## Examples

### Example: AWS Glue Integration

#### Frontend requirements

* Database selector
* Table selector
* Environment awareness

#### Fake API endpoints

```http
GET /api/plugins
GET /api/plugins/aws_glue
POST /api/data_products/{id}/outputs
```

#### Example response

```json
{
    "ui_metadata": [
      {
        "label": "Database",
        "type": "select",
        "required": true,
        "name": "database",
        "tooltip": null,
        "initial_value": null,
        "depends_on": null,
        "max_count": 1,
        "disabled": null,
        "use_namespace_when_not_source_aligned": true,
      },
      {
        "label": "Database suffix",
        "type": "string",
        "required": false,
        "name": "database_suffix",
        "tooltip": "The name of the database to give write access to. Defaults to data product namespace",
        "initial_value": null,
        "depends_on": null,
        "max_count": null,
        "disabled": null,
        "use_namespace_when_not_source_aligned": null,
      },
      {
        "label": "Entire schema",
        "type": "checkbox",
        "required": false,
        "name": "entire_schema",
        "tooltip": "Give write access to the entire schema instead of a single table",
        "initial_value": true,
        "depends_on": null,
        "max_count": null,
        "disabled": null,
        "use_namespace_when_not_source_aligned": null,
      },
      {
        "label": "Table",
        "type": "string",
        "required": true,
        "name": "table",
        "tooltip": "The name of the table to give write access to",
        "initial_value": null,
        "depends_on": {
          "field_name": "entire_schema",
          "value": false
        },
        "max_count": null,
        "disabled": null,
        "use_namespace_when_not_source_aligned": null,
      }
    ],
    "plugin": "GlueDataOutput",
    "result_label": "Resulting table",
    "result_tooltip": "The table you can access through this technical asset",
    "platform": "glue",
    "display_name": "Glue",
    "icon_name": "glue-logo.svg",
    "parent_platform": "aws",
    "platform_tile": null
  }
```

#### Database representation

```json
{
  "plugin": "aws_glue",
  "version": "1.0",
  "configuration": {
    "database": "pharma_research",
    "database_suffix": "analytics",
    "table": "*",
    "database_path": "pharma_research",
    "table_path": "*",
    "bucket_identifier": "datalake"
  }
}
```

---

## Pseudocode

### Plugin base class

```python
class UIElementType(str, Enum):
    String = "string"
    Select = "select"
    Checkbox = "checkbox"


class FieldDependency(ORMModel):
    """Represents a field dependency for conditional visibility"""

    field_name: str
    value: Any

class UIElementMetadata(ORMModel):
    label: str
    type: UIElementType
    required: bool
    name: str
    tooltip: Optional[str] = None
    initial_value: Optional[str | int | float | bool] = None
    depends_on: Optional[FieldDependency] = None
    max_count: Optional[int] = None
    disabled: Optional[bool] = None
    use_namespace_when_not_source_aligned: Optional[bool] = None

class AssetProviderPlugin(BaseModel):
    name: ClassVar[str]
    version: ClassVar[str]

    @classmethod
    def get_ui_metadata(cls) -> List[UIElementMetadata]:
        raise NotImplementedError

    def validate(self):
        pass

    def render_template(self, template, **context) -> str:
        pass

    def get_configuration(
        self, configs
    ): # Returns platform specific information
        pass

    def get_url(self, environment):
        pass

    def get_logo(self):
        pass

    def has_environnments(self) -> bool:
        pass

    # Future work
    def infra_provisioning(self):
        pass
```

### Registry discovery

```python
ENV_PLUGINS = [GlueProviderPlugin]

def discover_plugins():
    for cls in ENV_PLUGINS:
        registry.register(cls.name, cls)
```

### API exposure

```python
@app.get("/api/plugins")
def list_plugins():
    return registry.as_json()
```

---

## Pros and Cons of the Options

### Option: Python Plugin Architecture

* **Good, because** it introduces a clear abstraction and removes hardcoded logic
* **Good, because** backend validation and frontend generation are aligned
* **Bad, because** plugin complexity must be actively constrained

### Option 1: Strict Columns, one table

* **Good, because** migrations are explicit and predictable
* **Bad, because** every new integration requires schema changes
* **Bad, because** encourages incorrect abstraction mappings

### Option 2: JSON Blobs

* **Good, because** new integrations require no database migrations
* **Good, because** configuration matches technology terminology exactly
* **Bad, because** long-term migrations become more complex

### Option 3: Strict columns, table per plugin

* **Good, because** best of both options
* **Good, because** Allow mapping of technology terminology to database columns exactly
* **Good, because** Easier long-term migrations.
* **Bad, because** Developer needs to provide migration per new plugin.

---

## Pros and Cons of the Plugin Provisioning Options

### Option 1: Internal Plugins Only

* **Good, because** simplest operational model
* **Good, because** full control over code quality and security
* **Bad, because** requires contributing to core codebase

### Option 2: Installable Plugins (Chosen Direction)

* **Good, because** aligns with Python standards (`pip install`)
* **Good, because** no rebuild required, restart is sufficient
* **Good, because** prepares us for the future.
* **Bad, because** shared dependency conflicts are possible
* **Bad, because** versioning discipline is required
* **Bad, because** slightly more complex initial implementation
