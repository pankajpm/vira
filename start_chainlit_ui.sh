#!/bin/bash
# Start VIRA Chainlit UI

set -e

echo "🚀 Starting VIRA Chainlit UI..."
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: No virtual environment detected."
    echo "   Consider activating your venv first."
    echo ""
fi

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY not set!"
    echo "   Export it or add to .env file"
    exit 1
fi

# Create data directory if it doesn't exist
mkdir -p ./data

# Initialize database if it doesn't exist
if [ ! -f "./data/vira_sessions.db" ]; then
    echo "📊 Initializing database..."
    python -c "from vira.ui.database.models import create_tables; create_tables()"
    echo "✅ Database created at ./data/vira_sessions.db"
    echo ""
fi

# Check if vector database exists
if [ ! -d "./data/processed/chroma" ]; then
    echo "⚠️  Warning: Vector database not found at ./data/processed/chroma/"
    echo "   Run ingestion pipeline first:"
    echo "   1. python -m vira.ingestion.runner crawl --config-path ./config/crawl_settings.yaml"
    echo "   2. python -m vira.processing.cli ingest --raw-path ./data/raw/a16z_raw.jsonl"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start Chainlit with auto-reload
echo "🌐 Starting Chainlit server..."
echo "   URL: http://localhost:8000"
echo "   Press Ctrl+C to stop"
echo ""

chainlit run src/vira/ui/chainlit_app.py -w

