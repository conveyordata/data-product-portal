# Plugin System: Production Deployment Guide

This guide explains how to deploy the Data Product Portal with plugins in production environments using Docker.

## Philosophy

The Data Product Portal backend is designed to be **distributed as a base image** that can be extended with plugins **without modification**. Plugins are installed at runtime, allowing organizations to:

- Use the official backend image without rebuilding
- Add custom/proprietary plugins without forking the codebase
- Install plugins from a marketplace or private registry
- Dynamically enable/disable plugins via configuration

## Architecture Overview

```
┌─────────────────────────────────────┐
│  Base Backend Image (Distributed)   │
│  - Core portal functionality        │
│  - Plugin discovery system          │
│  - Auto-migration support           │
└─────────────────────────────────────┘
              ↓ extends
┌─────────────────────────────────────┐
│  Runtime: Plugins Installed         │
│  - Via init container               │
│  - Via mounted volumes              │
│  - Via pip at startup               │
└─────────────────────────────────────┘
```

## Deployment Patterns

### Pattern 1: Init Container Installation (Recommended)

Install plugins via init containers before the main app starts. This keeps the base image unchanged while providing fast startup.

**Kubernetes Example:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: data-product-portal
spec:
  template:
    spec:
      # Shared volume for plugins
      volumes:
      - name: plugins
        emptyDir: {}
      - name: venv-site-packages
        emptyDir: {}

      initContainers:
      # 1. Install plugins into shared volume
      - name: install-plugins
        image: data-product-portal:latest
        command: ["/bin/sh", "-c"]
        args:
        - |
          echo "Installing plugins..."
          pip install \
            data-product-portal-s3-plugin==1.0.0 \
            data-product-portal-custom-plugin==2.1.0 \
            --target=/plugins-site-packages

          echo "Copying plugin migrations..."
          cp /plugins-site-packages/*/migration/*.py \
             /app/app/database/alembic/versions/ || true

          echo "Plugins installed successfully"
        volumeMounts:
        - name: venv-site-packages
          mountPath: /plugins-site-packages
        env:
        # Optional: Use private PyPI repository
        - name: PIP_INDEX_URL
          value: "https://pypi.your-org.com/simple"

      # 2. Run database migrations
      - name: migrate
        image: data-product-portal:latest
        command: ["alembic", "upgrade", "head"]
        volumeMounts:
        - name: venv-site-packages
          mountPath: /plugins-site-packages
        env:
        - name: PYTHONPATH
          value: "/app:/plugins-site-packages"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: portal-secrets
              key: database-url

      containers:
      # 3. Main application
      - name: backend
        image: data-product-portal:latest
        volumeMounts:
        - name: venv-site-packages
          mountPath: /plugins-site-packages
        env:
        - name: PYTHONPATH
          value: "/app:/plugins-site-packages"
        - name: AUTO_RUN_PLUGIN_MIGRATIONS
          value: "false"  # Already ran in init container
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: portal-secrets
              key: database-url
```

**Docker Compose Example:**

```yaml
version: '3.8'

services:
  # Init service to install plugins
  plugin-installer:
    image: data-product-portal:latest
    command: >
      sh -c "
        pip install --target=/plugins
          data-product-portal-s3-plugin==1.0.0
          data-product-portal-custom-plugin==2.1.0 &&
        cp /plugins/*/migration/*.py /migrations/ || true
      "
    volumes:
      - plugin-packages:/plugins
      - plugin-migrations:/migrations

  # Migration runner
  migrate:
    image: data-product-portal:latest
    command: alembic upgrade head
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/portal
      - PYTHONPATH=/app:/plugins
    volumes:
      - plugin-packages:/plugins:ro
      - plugin-migrations:/app/app/database/alembic/versions/plugins:ro
    depends_on:
      plugin-installer:
        condition: service_completed_successfully
      db:
        condition: service_healthy

  # Main application
  backend:
    image: data-product-portal:latest
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/portal
      - PYTHONPATH=/app:/plugins
      - AUTO_RUN_PLUGIN_MIGRATIONS=false
    volumes:
      - plugin-packages:/plugins:ro
      - plugin-migrations:/app/app/database/alembic/versions/plugins:ro
    ports:
      - "8000:8000"
    depends_on:
      migrate:
        condition: service_completed_successfully

  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_DB: portal
    healthcheck:
      test: ["CMD-EXEC", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  plugin-packages:
  plugin-migrations:
```

### Pattern 2: Volume-Mounted Plugins

Mount pre-built plugin wheels from a persistent volume. Good for airgapped environments.

**Setup:**

```bash
# 1. Build plugin wheels externally
cd plugins/s3_plugin
python -m build --wheel
# Produces: dist/data_product_portal_s3_plugin-1.0.0-py3-none-any.whl

# 2. Copy to shared storage
cp dist/*.whl /mnt/portal-plugins/

# 3. Deploy with volume mount
```

**Kubernetes PersistentVolume:**

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: portal-plugins
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadOnlyMany
  nfs:
    server: nfs-server.example.com
    path: /exports/portal-plugins

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: portal-plugins-claim
spec:
  accessModes:
    - ReadOnlyMany
  resources:
    requests:
      storage: 1Gi

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: data-product-portal
spec:
  template:
    spec:
      initContainers:
      - name: install-plugins
        image: data-product-portal:latest
        command: ["/bin/sh", "-c"]
        args:
        - |
          for wheel in /plugin-wheels/*.whl; do
            pip install "$wheel" --target=/plugins-site-packages
          done
        volumeMounts:
        - name: plugin-wheels
          mountPath: /plugin-wheels
          readOnly: true
        - name: site-packages
          mountPath: /plugins-site-packages

      containers:
      - name: backend
        image: data-product-portal:latest
        volumeMounts:
        - name: site-packages
          mountPath: /plugins-site-packages
        env:
        - name: PYTHONPATH
          value: "/app:/plugins-site-packages"

      volumes:
      - name: plugin-wheels
        persistentVolumeClaim:
          claimName: portal-plugins-claim
      - name: site-packages
        emptyDir: {}
```

### Pattern 3: Custom Extended Image (Optional)

For organizations that want to version their plugin stack, create a thin extension image:

```dockerfile
# Dockerfile.with-plugins
FROM data-product-portal:1.0.0

# Install plugins from PyPI or private registry
RUN pip install \
    data-product-portal-s3-plugin==1.0.0 \
    data-product-portal-custom-plugin==2.1.0

# Copy plugin migrations
RUN cp $(python -c "import s3_plugin; print(s3_plugin.__path__[0])")/migration/*.py \
       /app/app/database/alembic/versions/

# Metadata
LABEL org.opencontainers.image.title="Data Product Portal with S3 Plugin"
LABEL org.opencontainers.image.version="1.0.0-with-s3"
```

This creates a **new versioned image** without modifying the base, allowing rollback to the base image if needed.

## Plugin Distribution

## Plugin Distribution

### Public PyPI

Publish plugins to PyPI for public distribution:

```bash
cd plugins/s3_plugin
python -m build
twine upload dist/*
```

Install in production:
```yaml
initContainers:
- name: install-plugins
  command: ["pip", "install", "data-product-portal-s3-plugin==1.0.0"]
```

### Private PyPI / Artifactory

For proprietary plugins, use a private package repository:

```yaml
initContainers:
- name: install-plugins
  command:
  - pip
  - install
  - --index-url=https://pypi.yourcompany.com/simple
  - data-product-portal-custom-plugin==2.0.0
  env:
  - name: PIP_INDEX_URL
    value: "https://pypi.yourcompany.com/simple"
  - name: PIP_TRUSTED_HOST
    value: "pypi.yourcompany.com"
```

### Container Registry

Store plugin wheels as artifacts in container registry:

```bash
# Package plugin as artifact
tar czf s3-plugin.tar.gz -C plugins/s3_plugin/dist .

# Push to registry (e.g., GitHub Packages, GitLab Container Registry)
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
docker run --rm -v $(pwd):/workspace alpine sh -c \
  "cat /workspace/s3-plugin.tar.gz" | \
  docker image load --input - | \
  docker tag - ghcr.io/yourorg/portal-plugins/s3:1.0.0
docker push ghcr.io/yourorg/portal-plugins/s3:1.0.0
```

### Plugin Marketplace (Future)
```
plugins/your-plugin/
├── pyproject.toml
├── README.md
├── your_plugin/
│   ├── __init__.py
│   ├── schema.py
│   ├── model.py
│   └── migration/
│       └── 2026_xx_xx_xxxx_your_plugin.py
```

2. **Define dependencies** in `pyproject.toml`:
```toml
[project]
name = "data-product-portal-your-plugin"
version = "1.0.0"
dependencies = [
    "pydantic>=2.0.0",
    "sqlalchemy>=2.0.0",
    # Add your specific dependencies
]

[project.entry-points."data_product_portal.plugins"]
YourTechnicalAssetConfiguration = "your_plugin.schema:YourTechnicalAssetConfiguration"
```

3. **Test locally** using editable install:
```bash
cd backend
poetry run pip install -e ../plugins/your-plugin
```

### Docker Build (Multi-stage)

Create a `Dockerfile` that installs plugins at build time:

```dockerfile
# Stage 1: Build environment
FROM python:3.13-slim as builder

WORKDIR /app

# Copy backend and plugin source
COPY backend/ /app/backend/
COPY plugins/ /app/plugins/

# Install poetry
RUN pip install poetry

# Install backend dependencies
WORKDIR /app/backend
RUN poetry config virtualenvs.in-project true && \
    poetry install --only main --no-root

# Install plugins
RUN poetry run pip install /app/plugins/s3_plugin/ && \
    poetry run pip install /app/plugins/your-plugin/

# Stage 2: Runtime environment
FROM python:3.13-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/backend/.venv /app/.venv
COPY backend/app /app/app
COPY backend/alembic.ini /app/
COPY backend/pyproject.toml /app/

# Copy plugin migrations to the alembic versions folder
COPY --from=builder /app/plugins/*/migration/*.py /app/app/database/alembic/versions/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Configuration

Set environment variables to control plugin loading:

```bash
# Enable specific plugins (comma-separated)
ENABLED_PLUGINS="s3_plugin.schema.S3TechnicalAssetConfiguration,your_plugin.schema.YourTechnicalAssetConfiguration"

# Auto-run migrations on startup
AUTO_RUN_PLUGIN_MIGRATIONS=true
```

### Docker Compose Example

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/portal
      - AUTO_RUN_PLUGIN_MIGRATIONS=true
      - ENABLED_PLUGINS=s3_plugin.schema.S3TechnicalAssetConfiguration
    ports:
      - "8000:8000"
    depends_on:
      - db

  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_DB: portal
```

## Pattern 2: External Plugins with Volumes

For dynamic plugin loading without rebuilding images:

### Directory Structure

```
/opt/portal/
├── plugins/
│   ├── s3_plugin/
│   └── custom_plugin/
```

### Docker Compose with Volumes

```yaml
services:
  backend:
    image: data-product-portal:latest
    volumes:
      # Mount plugins directory
      - /opt/portal/plugins:/app/plugins:ro
      # Mount plugin migrations
      - /opt/portal/plugins/s3_plugin/migration:/app/app/database/alembic/versions/plugins:ro
    environment:
      # Plugins will be auto-discovered via entry points
      - AUTO_RUN_PLUGIN_MIGRATIONS=true
      - PYTHONPATH=/app:/app/plugins
```

### Installation Script

Create an init container or startup script to install plugins:

```bash
#!/bin/bash
# install-plugins.sh

for plugin_dir in /app/plugins/*/; do
    if [ -f "$plugin_dir/pyproject.toml" ]; then
        echo "Installing plugin from $plugin_dir"
        pip install "$plugin_dir"
    fi
done

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Update Dockerfile:
```dockerfile
COPY install-plugins.sh /app/
RUN chmod +x /app/install-plugins.sh
CMD ["/app/install-plugins.sh"]
```

## Pattern 3: Custom Docker Image Layers

For maximum flexibility, extend the base image:

### Base Image

```dockerfile
# Dockerfile.base
FROM python:3.13-slim

WORKDIR /app
COPY backend/ /app/
RUN pip install poetry && \
    poetry config virtualenvs.in-project true && \
    poetry install --only main --no-root

ENV PATH="/app/.venv/bin:$PATH"
```

### Plugin Extension Image

```dockerfile
# Dockerfile.with-s3-plugin
FROM data-product-portal:base

# Install S3 plugin
COPY plugins/s3_plugin /tmp/s3_plugin
RUN pip install /tmp/s3_plugin && rm -rf /tmp/s3_plugin

# Copy migration
COPY plugins/s3_plugin/migration/*.py /app/app/database/alembic/versions/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build separately:
```bash
docker build -f Dockerfile.base -t data-product-portal:base .
docker build -f Dockerfile.with-s3-plugin -t data-product-portal:with-s3 .
```

## Plugin Development Without Backend Codebase

### Standalone Plugin Development

You **do** need the backend types for development, but can install it as a package:

```bash
# In your plugin directory
pip install git+https://github.com/your-org/data-product-portal.git@main#subdirectory=backend
```

Or use a published wheel:
```toml
[project]
dependencies = [
    "data-product-portal-backend>=1.0.0",
    "pydantic>=2.0.0",
    "sqlalchemy>=2.0.0",
]
```

### Plugin Marketplace (Future)

Consider building a plugin marketplace:
- Web UI to browse available plugins
- Version compatibility matrix
- Automated testing and certification
- Usage analytics and ratings

## Plugin Development

### Development Without Backend Source

Developers can create plugins without the full backend codebase:

**Option 1: Install backend as package**

```bash
# Create plugin project
mkdir my-custom-plugin
cd my-custom-plugin

# Install backend SDK
pip install data-product-portal-sdk  # When published

# Or from git
pip install git+https://github.com/data-minded/data-product-portal.git@main#subdirectory=backend
```

**Option 2: Use types-only package**

Publish a types-only package for plugin development:

```toml
# data-product-portal-types package
[project]
name = "data-product-portal-types"
dependencies = [
    "pydantic>=2.0.0",
    "sqlalchemy>=2.0.0",
]
```

### Plugin Development Structure

```
my-custom-plugin/
├── pyproject.toml
├── README.md
├── LICENSE
├── my_plugin/
│   ├── __init__.py
│   ├── schema.py          # Plugin configuration
│   ├── model.py           # SQLAlchemy model
│   └── migration/
│       └── 2026_xx_xx_xxxx_my_plugin.py
├── tests/
│   ├── test_schema.py
│   └── test_integration.py
└── docs/
    ├── installation.md
    └── configuration.md
```

### Plugin Template

```python
# my_plugin/schema.py
from typing import ClassVar, Literal
from app.data_output_configuration.base_schema import (
    AssetProviderPlugin,
    PlatformMetadata,
)
from app.data_output_configuration.data_output_types import DataOutputTypes

class MyCustomTechnicalAssetConfiguration(AssetProviderPlugin):
    name: ClassVar[str] = "MyCustomTechnicalAssetConfiguration"
    version: ClassVar[str] = "1.0.0"
    migration_file_path: ClassVar[str] = (
        "app/database/alembic/versions/2026_xx_xx_xxxx_my_custom.py"
    )

    # Plugin-specific fields
    endpoint: str
    api_key: str
    configuration_type: Literal[DataOutputTypes.MyCustomTechnicalAssetConfiguration]

    _platform_metadata = PlatformMetadata(
        display_name="My Custom Platform",
        icon_name="custom-logo.svg",
        platform_key="custom",
    )
```

**pyproject.toml:**

```toml
[project]
name = "data-product-portal-my-plugin"
version = "1.0.0"
description = "Custom platform integration for Data Product Portal"
requires-python = ">=3.10"
dependencies = [
    "pydantic>=2.0.0",
    "sqlalchemy>=2.0.0",
]

[project.entry-points."data_product_portal.plugins"]
MyCustomTechnicalAssetConfiguration = "my_plugin.schema:MyCustomTechnicalAssetConfiguration"

[project.optional-dependencies]
dev = [
    "data-product-portal-backend",  # For local development
    "pytest",
    "pytest-cov",
]
```

## Configuration Management

### Environment-Based Plugin Selection

Enable different plugins per environment:

```yaml
# production.env
ENABLED_PLUGINS=s3_plugin.schema.S3TechnicalAssetConfiguration,snowflake_plugin.schema.SnowflakeTechnicalAssetConfiguration

# staging.env
ENABLED_PLUGINS=s3_plugin.schema.S3TechnicalAssetConfiguration,custom_plugin.schema.CustomTechnicalAssetConfiguration

# development.env
ENABLED_PLUGINS=  # Empty = auto-discover all
```

### ConfigMap for Plugin Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: portal-plugin-config
data:
  enabled-plugins: |
    s3_plugin.schema.S3TechnicalAssetConfiguration
    snowflake_plugin.schema.SnowflakeTechnicalAssetConfiguration

  plugin-versions: |
    s3_plugin: 1.0.0
    snowflake_plugin: 2.1.0

  auto-migrate: "false"

---
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: backend
        envFrom:
        - configMapRef:
            name: portal-plugin-config
```

## Migration Management

### Production Migration Strategy

**DO NOT** use auto-migrations in production:

```yaml
env:
- name: AUTO_RUN_PLUGIN_MIGRATIONS
  value: "false"
```

**Instead**, run migrations in init container:

```yaml
initContainers:
- name: migrate
  image: data-product-portal:latest
  command: ["alembic", "upgrade", "head"]
  volumeMounts:
  - name: plugins
    mountPath: /plugins
  env:
  - name: PYTHONPATH
    value: "/app:/plugins"
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: portal-secrets
        key: database-url
```

### Migration Rollback

To rollback a plugin migration:

```bash
# Identify the migration to rollback to
kubectl exec -it portal-backend-xxx -- alembic history

# Rollback
kubectl exec -it portal-backend-xxx -- alembic downgrade <revision>

# Remove plugin
kubectl set env deployment/portal ENABLED_PLUGINS=""
```

## Monitoring & Observability

### Plugin Health Checks

Add health endpoint that reports plugin status:

```python
# In backend
@router.get("/health/plugins")
def plugin_health():
    return {
        "total_plugins": len(PluginRegistry.get_all()),
        "plugins": [
            {
                "name": p.__name__,
                "version": getattr(p, "version", "unknown"),
                "healthy": True,  # Add health check logic
            }
            for p in PluginRegistry.get_all()
        ]
    }
```

Monitor in Kubernetes:

```yaml
livenessProbe:
  httpGet:
    path: /api/v2/health/plugins
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 60
```

### Metrics

Track plugin usage:

```python
# Add to your metrics
plugin_requests_total = Counter(
    'portal_plugin_requests_total',
    'Total requests per plugin type',
    ['plugin_name']
)
```

## Security

### Plugin Verification

Verify plugin signatures before installation:

```bash
# Sign plugin wheel
gpg --detach-sign dist/my_plugin-1.0.0-py3-none-any.whl

# Verify in init container
gpg --verify /plugin-wheels/my_plugin-1.0.0-py3-none-any.whl.sig
pip install /plugin-wheels/my_plugin-1.0.0-py3-none-any.whl
```

### Dependency Scanning

Scan plugin dependencies:

```yaml
# In CI/CD
- name: Scan plugin dependencies
  run: |
    pip install safety
    safety check --file requirements.txt
```

### Network Policies

Restrict plugin network access:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: portal-backend
spec:
  podSelector:
    matchLabels:
      app: portal-backend
  policyTypes:
  - Egress
  egress:
  # Allow database
  - to:
    - podSelector:
        matchLabels:
          app: postgresql
    ports:
    - protocol: TCP
      port: 5432
  # Allow plugin API calls (if needed)
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443
```

## CI/CD Integration

### GitOps Workflow

```yaml
# .github/workflows/deploy-with-plugins.yml
name: Deploy Portal with Plugins

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Update plugin versions in ConfigMap
      run: |
        kubectl create configmap portal-plugin-config \
          --from-literal=plugins="s3:1.0.0,custom:2.0.0" \
          --dry-run=client -o yaml | kubectl apply -f -

    - name: Restart deployment to pick up new plugins
      run: kubectl rollout restart deployment/portal-backend

    - name: Wait for rollout
      run: kubectl rollout status deployment/portal-backend

    - name: Verify plugins loaded
      run: |
        kubectl exec deployment/portal-backend -- \
          python -c "from app.data_output_configuration.registry import PluginRegistry; \
                     print(f'Loaded {len(PluginRegistry.get_all())} plugins')"
```

### Automated Testing

Test backend with different plugin combinations:

```yaml
# tests/plugin-combinations.yaml
test_matrix:
  - plugins: [s3, snowflake]
    expected_count: 2
  - plugins: [s3, snowflake, databricks]
    expected_count: 3
  - plugins: []
    expected_count: 4  # Built-in plugins only
```

## Best Practices

### ✅ DO

1. **Keep base image minimal** - Don't bundle plugins in base image
2. **Version plugins independently** - Each plugin has its own version
3. **Use init containers** - Install plugins before app starts
4. **Disable auto-migrations in prod** - Run migrations explicitly
5. **Test plugin compatibility** - Verify plugins work with backend version
6. **Document dependencies** - Clear plugin requirements
7. **Sign plugin packages** - Verify authenticity
8. **Monitor plugin health** - Add observability
9. **Use semantic versioning** - Clear version compatibility
10. **Provide rollback plan** - Document how to remove plugins

### ❌ DON'T

1. **Don't rebuild base image for plugins** - Defeats the purpose
2. **Don't mix plugin versions** - Use consistent versions across replicas
3. **Don't skip migration testing** - Always test in staging first
4. **Don't hardcode plugin paths** - Use environment variables
5. **Don't run untrusted plugins** - Verify source and dependencies
6. **Don't auto-migrate in production** - Use init containers
7. **Don't forget cleanup** - Remove unused plugin data
8. **Don't skip health checks** - Monitor plugin status
9. **Don't ignore dependencies** - Pin versions explicitly
10. **Don't deploy without testing** - Test plugin combinations

## Troubleshooting

### Plugin not discovered
```bash
# Check if plugin is installed
kubectl exec -it portal-backend-xxx -- pip list | grep my-plugin

# Check entry points
kubectl exec -it portal-backend-xxx -- python -c \
  "from importlib.metadata import entry_points; \
   print([ep for ep in entry_points().get('data_product_portal.plugins', [])])"

# Check PYTHONPATH
kubectl exec -it portal-backend-xxx -- env | grep PYTHONPATH
```

### Migration fails
```bash
# Check migration file exists
kubectl exec -it portal-backend-xxx -- \
  ls -la /app/app/database/alembic/versions/

# Check alembic status
kubectl exec -it portal-backend-xxx -- alembic current

# Check pending migrations
kubectl exec -it portal-backend-xxx -- alembic history
```

### Import errors
```bash
# Verify plugin module is importable
kubectl exec -it portal-backend-xxx -- python -c \
  "from my_plugin.schema import MyPlugin; print('OK')"

# Check for dependency conflicts
kubectl exec -it portal-backend-xxx -- pip check
```

## Summary

**Recommended Production Architecture:**

```
1. Distribute base backend image (unchanged)
   ↓
2. Install plugins via init container
   ↓
3. Run migrations in init container
   ↓
4. Start application with plugins loaded
```

**Key Benefits:**
- ✅ Base image never changes
- ✅ Plugins distributed independently
- ✅ Easy to add/remove plugins
- ✅ Clear version management
- ✅ Supports plugin marketplace
- ✅ Works in air-gapped environments
- ✅ Rollback-friendly architecture

**Example deployment:**
```bash
# 1. Publish base image
docker push yourregistry.com/data-product-portal:1.0.0

# 2. Publish plugins to PyPI
twine upload dist/data_product_portal_s3_plugin-1.0.0.tar.gz

# 3. Deploy with plugins
kubectl apply -f k8s/deployment.yaml  # Uses init container to install plugins

# 4. Plugins are loaded at runtime, base image unchanged
```

This architecture enables a true **plugin ecosystem** where the core remains stable and extensions can be developed, distributed, and installed independently.
