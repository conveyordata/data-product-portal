# Adding Integrations to the Data Product Portal

**Warning**: Installations older than portal 0.7.3 must upgrade to 0.7.3 before moving to 0.8.0, because the technical asset tables changed and the older migration logic is gone; see the [release notes](../release-notes.md).

**Warning**: Provisioners must switch their technical asset imports from `sdk.api_client.models` to `sdk.plugins`, because plugin classes are no longer known when the API is generated; see the [release notes](../release-notes.md).

Your data products live on real tools: a database in Glue, a bucket in S3, a repository in GitHub. Integrations connect the portal to those tools. They let a data product owner register the resources their product owns, and they give everyone a quick link from the data product page to the tool itself.

The portal ships with a set of integrations out of the box (see [Integrations](./integrations.md)). If the tool you use isn't among them, you can write your own as a plugin. A plugin is a small Python package that you install next to the portal. The portal picks it up when it starts, so you don't have to change the portal's code or maintain a fork of it.


This guide uses the [Glue plugin](https://github.com/conveyordata/data-product-portal/tree/main/plugins/portal_plugins/glue) as its running example. With it, a data product owner registers a Glue database as a [technical asset](../concepts/technical-assets.md) of their product. It lives in its own package, [`plugins/`](https://github.com/conveyordata/data-product-portal/tree/main/plugins), and registers itself the same way this guide describes, so it's the best place to see complete, working code. Because it sits in the portal's own repository, it doesn't list `data-product-portal` as a dependency, but yours should. Still we believe it to be a good reference

## Step 1: Install the portal package

Building a plugin starts with installing the `data-product-portal` package from PyPI. It is published with every release since 0.8.0 and contains everything you need to build a plugin, and more: the base class your plugin extends, the building blocks for forms, and access to the portal's environments and platforms.

Always use the same version as the portal you run. If your portal runs 0.8.0, install 0.8.0. The portal image already contains this package, so a matching version means nothing gets replaced when your plugin is installed into it later.

Create a new project and add the package. Depending on the package manager you use:

With Poetry:

```bash
poetry new my-portal-plugins
cd my-portal-plugins
poetry add "data-product-portal==0.8.0"
```

With uv:

```bash
uv init --lib my-portal-plugins
cd my-portal-plugins
uv add data-product-portal>=0.8.0
```

With setuptools, list it in `install_requires` in your `setup.py`, and install it into your environment:

```bash
pip install data-product-portal==0.8.0
```

A plugin package can hold one plugin or several. Each one gets its own folder:

```
my_portal_plugins/
└── glue/
    ├── schema.py        # the plugin class
    ├── model.py         # the database table
    ├── glue-logo.svg    # the icon shown in the portal
    └── versions/        # database migrations
        └── glue_0001_baseline.py
```

## Step 2: Write your plugin

Every plugin is a Python class that extends `TechnicalAssetPlugin`. The class tells the portal what the plugin is called, how it looks in the portal, what a data product owner fills in, and where that gets stored.
The [Glue plugin's `schema.py`](https://github.com/conveyordata/data-product-portal/blob/main/plugins/portal_plugins/glue/schema.py) has the full code. Its outline looks like this:

```python
class GlueTechnicalAssetConfiguration(TechnicalAssetPlugin):
    name: ClassVar[str] = "GlueTechnicalAssetConfiguration"

    # the values the owner fills in, these are handpicked for Glue so yours will look different.
    database: str
    table: str = "*"

    # This is platform metadata, that helps the portal show the plugin in the right place.
    _platform_metadata = PlatformMetadata(display_name="Glue", parent_platform="aws", ...)

    class Meta:
        orm_model = GlueModel  # the table that stores the values

    @classmethod
    def get_ui_metadata(cls, db):
        # describe the form: one UIElementMetadata per field

    def validate_configuration(self, data_product, db):
        # raise an error if the input isn't acceptable

    def get_configuration(self, configs):
        # pick the settings that belong to this asset
```

The sections below go through this outline one part at a time, in the order you'd build it.

### The name and the tile

`name` identifies your plugin. It has to be unique among all plugins in your portal, and you'll use it again when you enable the plugin in step 4.

`_platform_metadata` describes how your plugin looks in the portal. Every plugin shows up as a tile, and these are the settings you'll use most:

- `display_name` is the label on the tile, such as "Glue".
- `icon_name` and `icon_package` point to the tile's icon. Every plugin brings its own icon: put the SVG file in your plugin's folder, set `icon_name` to the file name, and set `icon_package` to the Python package that holds it, for example `my_portal_plugins.glue`. The portal reads the file from your package.
- `parent_platform` groups the tile under another one. Glue appears under AWS.
- `platform_key` links the plugin to its platform service, explained in the next section.
- `has_environments` decides whether the tile lets you pick an environment, such as development or production. It's on by default.
- `show_in_form` decides whether the plugin appears in the form for creating a technical asset. It's on by default.

If you override `get_url`, the tile opens a link, for example to the resource in its own tool.

Those are the only parts every plugin needs. A plugin that only has a name, a tile and `get_url` adds a link from the data product page to another tool. Set `show_in_form=False` and `has_environments=False` for that, and skip the rest of this step. The [GitHub plugin](https://github.com/conveyordata/data-product-portal/blob/main/backend/app/technical_asset_configuration/github/schema.py) works like this.

### The platform and platform service

When a data product owner creates a Glue technical asset, they pick a database from a dropdown. That list has to come from somewhere, and the right AWS account for each environment too. The portal keeps this information in three places:

- A platform is a technology vendor or cloud provider, such as AWS, Azure, Databricks or Snowflake.
- A platform service is one service of a platform, such as S3 or Glue on AWS. It holds the list of options your form offers, for example `["datalake", "ingress", "egress"]`. It also holds `result_string_template`, which turns what the owner filled in into the name everyone sees, such as `{bucket}/{path}` for S3. The names between braces are your plugin's fields.
- An environment is a stage such as development or production. Per environment it contains the settings that differ, such as the AWS account and region, or which real bucket belongs to each option. They're linked to an option through its `identifier`.


Your plugin uses this in two places. `get_platform_options` reads the list of options, to fill a dropdown in your form. `get_configuration` gets the settings of the chosen environment, and returns the entry that belongs to this asset, usually the one whose `identifier` matches what the owner picked. The portal already knows the format of these environment settings for the platforms it supports, such as `AWSGlueConfig` for Glue. A plugin for another tool can reuse one of them, or do without environment settings by setting `has_environments=False`.

These rows live in the portal's database, and you add them with SQL. A plugin that only adds a link needs none of them:

| Table | What goes in it | Needed for a plugin with a form |
|---|---|---|
| `platforms` | The platform, such as AWS | Yes |
| `platform_services` | The platform service, with its templates | Yes |
| `platform_service_configs` | The list of options | Yes, use `'[]'` if there are none |
| `env_platform_configs` | Platform settings per environment | Only if `has_environments=True` |
| `env_platform_service_configs` | Platform service settings per environment | Only if `has_environments=True` |

The portal finds these rows by name, so two names have to match your `_platform_metadata`, ignoring upper and lower case. If they don't, the form can't find your platform and creating a technical asset fails:

- The platform service's `name` has to equal `platform_key`.
- The platform's `name` has to equal the tile it sits under: `parent_platform` if you set one, otherwise `display_name`.

For Glue, which sits under AWS, that looks like this:

```sql
INSERT INTO platforms (name) VALUES ('AWS');                          -- matches parent_platform "aws"
INSERT INTO platform_services (name, platform_id, result_string_template, technical_info_template)
VALUES ('Glue', <aws_id>, '{database}.{table}', '...');                -- matches platform_key "glue"
INSERT INTO platform_service_configs (platform_id, service_id, config)
VALUES (<aws_id>, <glue_id>, '["datalake", "ingress"]');
```

The demo seed file [`demo/basic/portal_seed.sql`](https://github.com/conveyordata/data-product-portal/blob/main/demo/basic/portal_seed.sql) has complete examples, including the settings per environment.

### The fields and the form

The fields, `database` and `table` for Glue, are what a data product owner fills in for one technical asset. You pick them for your own tool.

`get_ui_metadata` describes the form that asks for them. Each field in the form is one `UIElementMetadata`: a dropdown, a text box, a checkbox or a set of radio buttons, and it can depend on the value of another field. The portal draws the form for you, so you never write frontend code. A dropdown filled with the platform service's options looks like this:

```python
UIElementMetadata(
    name="database",
    label="Database",
    type=UIElementType.Select,
    required=True,
    select=UIElementSelect(options=cls.get_platform_options(db)),
)
```

The Glue plugin also uses a text field, radio buttons and a field that only appears for one of those radio choices, so it's a good place to see the other types.

`validate_configuration` runs just before a technical asset is saved. Raise an error there when the input isn't acceptable. Glue, for example, only accepts databases that start with the data product's namespace. You can also override `render_template` if the name built from `result_string_template` needs some cleaning up.

### The database table

The values an owner fills in are stored in a table that belongs to your plugin. You describe it as a SQLAlchemy model in `model.py`, with one column per field, and point to it from `Meta.orm_model` in your plugin class. The model extends `BaseTechnicalAssetConfiguration`, which links each row to the portal's own record of the technical asset. Set `polymorphic_identity` to the plugin's `name`, so the portal knows which plugin a row belongs to:

```python
class GlueModel(BaseTechnicalAssetConfiguration):
    __tablename__ = "glue_technical_asset_configurations"
    __mapper_args__ = {"polymorphic_identity": "GlueTechnicalAssetConfiguration"}

    database: Mapped[str] = mapped_column(String, nullable=True)
    table: Mapped[str] = mapped_column(String, nullable=True)
```

The Glue plugin's [`model.py`](https://github.com/conveyordata/data-product-portal/blob/main/plugins/portal_plugins/glue/model.py) is the complete version.

### Migrations

The model describes the table, but something still has to create it in the database. That is what a migration does. The portal uses [Alembic](https://alembic.sqlalchemy.org/) for this, and runs your plugin's migrations together with its own every time it's deployed.

Put your migrations in a `versions/` folder next to the file with your plugin class. The portal looks for that folder automatically. Write the first migration by hand; Alembic can't generate it for you here. Copying the [Glue baseline migration](https://github.com/conveyordata/data-product-portal/blob/main/plugins/portal_plugins/glue/versions/glue_0001_baseline.py) and changing the columns is the easiest start. Its core is:

```python
revision = "glue_0001_baseline"
down_revision = None

def upgrade():
    op.create_table(
        "glue_technical_asset_configurations",
        sa.Column("id", UUID, sa.ForeignKey("data_output_configurations.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("database", sa.String()),
        ...
    )
```

A few things to keep in mind:

- The `id` column has to point to `data_output_configurations.id`, the portal's own record of each technical asset.
- Start each revision id with your plugin's name, like `glue_0001_baseline`. The portal and all plugins share one list of applied migrations, so ids have to be unique across all of them.
- The first migration has `down_revision = None`. Each later one points to the migration before it.
- When you add or change a field later, add a new migration to the same folder. It can also move or fill in existing data.

To try your migrations before you ship them, run `python -m app.db_tool migrate` against a local database. It brings the portal and every installed plugin up to date in one go.

If you ever uninstall a plugin, its table stays in the database. The migration step will then stop with an error, because it finds migrations for a plugin that is no longer there. Reinstall the plugin, or remove its rows from the `alembic_version` table if you don't need its history anymore.

### MCP tools

If your portal runs the MCP server, a plugin can add its own tools to it by overriding `register_mcp_tools`, and add to the server's instructions with the `mcp_instructions` attribute. The Glue plugin does both, see its [`mcp_tools.py`](https://github.com/conveyordata/data-product-portal/blob/main/plugins/portal_plugins/glue/mcp_tools.py).

## Step 3: Tell the portal about your plugin

The portal finds plugins through a standard Python feature called [entry points](https://packaging.python.org/en/latest/specifications/entry-points/). In your package settings, you list your plugin classes under the group `data_product_portal.plugins`. When the package is installed, the portal sees that list and loads your plugins.

Each entry has a name of your choice on the left, and the location of the class on the right, written as `module:Class`. The portal's own [`plugins/pyproject.toml`](https://github.com/conveyordata/data-product-portal/blob/main/plugins/pyproject.toml) is a working example.

With Poetry 2 or later, or with uv, add this to `pyproject.toml`:

```toml
[project.entry-points."data_product_portal.plugins"]
github = "my_portal_plugins.github.schema:GitHubPlugin"
glue = "my_portal_plugins.glue.schema:GlueTechnicalAssetConfiguration"
```

Poetry versions before 2.0 use a slightly different table:

```toml
[tool.poetry.plugins."data_product_portal.plugins"]
github = "my_portal_plugins.github.schema:GitHubPlugin"
```

With setuptools, add it to the `setup()` call in `setup.py`:

```python
entry_points={
    "data_product_portal.plugins": [
        "github = my_portal_plugins.github.schema:GitHubPlugin",
    ],
},
package_data={"": ["*.svg", "versions/*.py"]},
```

Your icons and the `versions/` folder have to be part of the package you build, or the portal can't find them. Setuptools leaves them out unless you list them in `package_data`, as above. Whichever tool you use, build the package and check its contents with `unzip -l dist/*.whl`.

## Step 4: Add the plugin to your portal

The portal runs as a Docker image, and your plugin has to be installed in that image. You don't need to rebuild the portal for this. Start from the official image and install your package on top of it:

```dockerfile
FROM public.ecr.aws/conveyordata/data-product-portal:0.8.0

RUN pip install my-portal-plugins==0.1.0
```

If your package isn't published to a package index, `COPY` the built wheel into the image and `pip install` that file instead.

Build the image and push it to your own registry. If you deploy with the Helm chart, point it at your image with `image.repository` and `image.tag`. The chart runs the database migrations from the same image before the portal starts, so your plugin's table is created on the first deploy.

If you are using k8s to deploy your image turn the plugin on by adding its `name` to the list of enabled plugins. With Helm, that is `enabled_plugins` in your values file:

```yaml
enabled_plugins:
  - GitHubPlugin
  - GlueTechnicalAssetConfiguration
```

If not, set the `ENABLED_PLUGINS` environment variable to a JSON list, such as `'["GitHubPlugin", "GlueTechnicalAssetConfiguration"]'`. Tihs will enable all the plugins you list.

A plugin that is installed but not enabled still gets its migrations, and technical assets that already exist keep working. It just won't show up for new ones.

## Check that it works

When the portal starts, it logs every plugin it found:

```
Discovered plugins: GitHubPlugin, GlueTechnicalAssetConfiguration, ...
```

If your plugin isn't in that list, the entry point from step 3 is usually the cause: check the group name and the `module:Class` path. If it is in the list but doesn't show up in the portal, check that its `name` is in the enabled plugins.
Other setup problems may appear either in startup logs or when the portal loads the plugin's metadata; use the reported error to identify the failing configuration.
