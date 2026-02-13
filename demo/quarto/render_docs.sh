#!/bin/bash
set -e

echo "📚 Quarto Documentation Renderer"
echo "Watching /products for documentation changes..."
echo ""

# Function to render a single data product's docs
render_docs() {
    local product_dir="$1"
    local product_name=$(basename "$product_dir")

    # Check if docs directory exists
    if [ ! -d "$product_dir/docs" ]; then
        return
    fi

    echo "📖 Rendering docs for: $product_name"

    # Check for _quarto.yml or index.qmd
    if [ -f "$product_dir/docs/_quarto.yml" ] || [ -f "$product_dir/docs/index.qmd" ]; then
        cd "$product_dir/docs"

        # Render to /rendered/{product_name}
        quarto render --output-dir "/rendered/$product_name" 2>&1 | sed "s/^/  /"

        if [ $? -eq 0 ]; then
            echo "  ✅ Rendered to /rendered/$product_name"
        else
            echo "  ❌ Failed to render $product_name"
        fi
    fi
}

# Initial render of all existing docs
echo "Running initial render..."
for product_dir in /products/*/; do
    if [ -d "$product_dir" ]; then
        render_docs "$product_dir"
    fi
done

echo ""
echo "✅ Initial render complete"
echo "🔄 Watching for changes..."
echo ""

# Watch for changes and re-render
while true; do
    # Use inotifywait if available, otherwise just sleep and re-render periodically
    if command -v inotifywait &> /dev/null; then
        inotifywait -r -e modify,create,delete /products/*/docs 2>/dev/null || true
        sleep 2  # Debounce

        echo "📝 Change detected, re-rendering..."
        for product_dir in /products/*/; do
            if [ -d "$product_dir" ]; then
                render_docs "$product_dir"
            fi
        done
    else
        # Fallback: re-render every 60 seconds
        sleep 60
        for product_dir in /products/*/; do
            if [ -d "$product_dir" ]; then
                render_docs "$product_dir"
            fi
        done
    fi
done
