#!/bin/bash
# SQLMesh Pipeline Runner for {{ cookiecutter.project_name }}

set -e

echo "🔧 {{ cookiecutter.project_name }} - SQLMesh Pipeline"
echo "================================================"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "   This file should have been created by the provisioner"
    exit 1
fi

# Load environment variables
echo "📋 Loading S3 credentials from .env..."
export $(cat .env | grep -v '^#' | xargs)

echo "✅ Credentials loaded:"
echo "   S3_ENDPOINT_HOST: ${S3_ENDPOINT_HOST:-localhost}"
echo "   S3_BUCKET: $S3_BUCKET"
echo "   S3_PREFIX: $S3_PREFIX"
echo ""

# Check if SQLMesh is installed
if ! command -v sqlmesh &> /dev/null; then
    echo "⚠️  SQLMesh not found. Installing dependencies..."
    pip install 'sqlmesh[duckdb]' --quiet
    echo "✅ Dependencies installed"
    echo ""
fi

# Show info
echo "ℹ️  SQLMesh Configuration:"
sqlmesh info
echo ""

# Main menu loop
while true; do
    echo ""
    echo "What would you like to do?"
    echo "  1) Plan changes (preview what will run)"
    echo "  2) Run pipeline (execute transformations)"
    echo "  3) Validate models"
    echo "  4) Query results"
    echo "  5) Export to S3 (push data to MinIO)"
    echo "  6) Exit"
    echo ""
    read -p "Enter choice [1-6]: " choice

    case $choice in
        1)
            echo ""
            echo "📊 Planning SQLMesh execution..."
            sqlmesh plan
            ;;
        2)
            echo ""
            echo "🚀 Running SQLMesh pipeline..."
            sqlmesh run
            echo ""
            echo "✅ Pipeline complete!"

            # Ask if user wants to export to S3
            echo ""
            read -p "Export results to S3? (y/N): " export_choice
            if [[ $export_choice =~ ^[Yy]$ ]]; then
                echo ""
                echo "📦 Exporting data to S3..."
                python export_to_s3.py
            fi
            ;;
        3)
            echo ""
            echo "✅ Validating models..."
            sqlmesh validate
            ;;
        4)
            echo ""
            echo "💬 Opening interactive SQL console..."
            sqlmesh query
            ;;
        5)
            echo ""
            echo "📦 Exporting data to S3..."
            python export_to_s3.py
            ;;
        6)
            echo ""
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo ""
            echo "❌ Invalid choice. Please enter 1-6."
            ;;
    esac
done
