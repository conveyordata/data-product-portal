#!/bin/bash
set -e

echo "🚀 Starting Data Product Portal Demo POC"
echo ""

# Check if we're in the demo directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: Please run this script from the demo/ directory"
    exit 1
fi

# Check if backend is needed
echo "📋 Pre-flight checks..."

# Check if PostgreSQL is running
if ! docker compose -f ../compose.yaml ps postgresql | grep -q "Up"; then
    echo "⚠️  PostgreSQL is not running. Starting it now..."
    (cd .. && docker compose up postgresql -d)
    echo "⏳ Waiting for PostgreSQL to be ready..."
    sleep 5
fi

echo "✅ PostgreSQL is running"

# Check if backend is running
if ! curl -s http://localhost:5050/ > /dev/null 2>&1; then
    echo ""
    echo "⚠️  Portal backend is not running!"
    echo ""
    echo "Please start the backend with webhooks enabled:"
    echo ""
    echo "  cd backend"
    echo "  export WEBHOOK_URL=http://localhost:8090"
    echo "  export WEBHOOK_SECRET=demo-secret-key"
    echo "  python -m uvicorn app.main:app --reload --port 8080"
    echo ""
    echo "Press Enter to continue once the backend is running, or Ctrl+C to exit"
    read
fi

echo "✅ Portal backend is reachable"
echo ""

# Start demo services
echo "🐳 Starting demo services..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "✅ Demo stack is running!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Service URLs:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  🌐 Portal:         http://localhost:5050"
echo "  🔧 Provisioner:    http://localhost:8090"
echo "  🗄️  S3 Console:     http://localhost:9001"
echo "       Credentials:  minioadmin / minioadmin"
echo "  💻 Coder (VSCode): http://localhost:8443"
echo "       Password:     coder"
echo "  📈 RStudio:        http://localhost:8787"
echo "       Credentials:  rstudio / rstudio"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Next steps:"
echo "  1. Create a data product in the portal"
echo "  2. Check demo/products/ for the scaffolded project"
echo "  3. Open the project in Coder or RStudio"
echo ""
echo "📖 For more information, see demo/README.md"
echo ""
echo "🛑 To stop: docker compose down"
echo "📋 View logs: docker compose logs -f"
echo "🧹 Reset demo: ./clean.sh"
echo ""
