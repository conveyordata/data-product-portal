# Quarto Documentation Service

This directory contains the Quarto documentation rendering service for data products.

## Architecture

- **quarto** container: Watches `/products` directory and renders Quarto docs to `/rendered`
- **docs** container: Nginx server that serves rendered docs at `http://localhost:8888`

## How It Works

1. When a data product is created, the provisioner scaffolds a `docs/` directory with Quarto files
2. The quarto container detects the new docs and renders them to HTML
3. Rendered docs are stored in a shared volume
4. Nginx serves the docs at `/docs/{data-product-name}`

## Accessing Documentation

- **All docs**: http://localhost:8888/docs
- **Specific data product**: http://localhost:8888/docs/{data-product-name}

## Manual Rendering

To manually trigger a render for all data products:

```bash
docker compose exec quarto /app/render_docs.sh
```

To render a specific data product:

```bash
docker compose exec quarto sh -c "cd /products/{data-product-name}/docs && quarto render --output-dir /rendered/{data-product-name}"
```

## File Structure

```
products/
  my-data-product/
    docs/
      _quarto.yml      # Quarto project config
      index.qmd        # Home page
      data-dictionary.qmd
      usage-guide.qmd
      styles.css
```

## Customization

### Adding Pages

1. Create a new `.qmd` file in the data product's `docs/` directory
2. Add it to the navbar in `_quarto.yml`:
   ```yaml
   navbar:
     left:
       - text: "My New Page"
         href: my-new-page.qmd
   ```
3. The quarto container will auto-detect and render

### Styling

Edit `docs/styles.css` in your data product to customize the appearance.

## Troubleshooting

### Docs not appearing

1. Check quarto container logs: `docker compose logs quarto`
2. Verify docs directory exists: `ls products/{data-product-name}/docs`
3. Check rendered output: `docker compose exec quarto ls /rendered/{data-product-name}`

### Render errors

View detailed errors:
```bash
docker compose logs quarto -f
```

Common issues:
- Missing frontmatter in `.qmd` files
- Invalid YAML in `_quarto.yml`
- Python code errors in code blocks
