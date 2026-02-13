#!/bin/bash
set -e

echo "🧹 Data Product Portal Demo - Clean/Reset"
echo "=========================================="
echo ""
echo "This will:"
echo "  1. Stop all demo services"
echo "  2. Remove all scaffolded data products"
echo "  3. Clear MinIO S3 data"
echo "  4. Clear rendered documentation"
echo "  5. Remove Docker volumes"
echo "  6. Reset to clean state"
echo ""

# Confirm before proceeding
read -p "⚠️  This will DELETE all demo data. Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "🛑 Stopping services..."
docker compose down

echo ""
echo "🗑️  Removing scaffolded data products..."
if [ -d "./products" ]; then
    # Keep the directory but remove all contents
    find ./products -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} +
    echo "   Removed: $(pwd)/products/*"
else
    echo "   No products directory found"
fi

echo ""
echo "🗄️  Clearing S3 data..."
if [ -d "./s3" ]; then
    rm -rf ./s3
    mkdir -p ./s3
    echo "   Cleared: $(pwd)/s3/"
else
    mkdir -p ./s3
    echo "   Created: $(pwd)/s3/"
fi

echo ""
echo "📦 Removing Docker volumes..."
docker compose down -v 2>/dev/null || true

echo ""
echo "🏗️  Removing build cache (optional)..."
read -p "Remove Docker build cache? This will rebuild images from scratch. (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker compose build --no-cache
    echo "   ✅ Build cache cleared"
else
    echo "   Skipped build cache removal"
fi

echo ""
echo "✅ Demo reset complete!"
echo ""
echo "To start fresh:"
echo "  ./start.sh"
echo ""
echo "Or manually:"
echo "  docker compose up -d"
echo ""
