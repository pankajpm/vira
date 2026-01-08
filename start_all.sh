#!/bin/bash
# Start all VIRA services (backend, React frontend, Chainlit UI)

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="/tmp"
BACKEND_LOG="$LOG_DIR/vira-backend.log"
FRONTEND_LOG="$LOG_DIR/vira-frontend.log"
CHAINLIT_LOG="$LOG_DIR/vira-chainlit.log"

cd "$PROJECT_ROOT"

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

printf '\n🚀 Starting all VIRA services...\n\n'

# Start backend + React via existing script
bash "$PROJECT_ROOT/start_react_stack.sh"

printf '\n'

# Start Chainlit UI if not already running
if pgrep -f "chainlit run src/vira/ui/chainlit_app.py" > /dev/null; then
    echo "ℹ️  Chainlit already running. Skipping."
else
    if [ -z "${OPENAI_API_KEY:-}" ]; then
        echo "⚠️  OPENAI_API_KEY not set. Skipping Chainlit startup."
    else
        echo "🧱 Ensuring database prerequisites exist..."
        mkdir -p ./data
        if [ ! -f "./data/vira_sessions.db" ]; then
            python -c "from vira.ui.database.models import create_tables; create_tables()"
            echo "✅ Created ./data/vira_sessions.db"
        fi

        if [ ! -d "./data/processed/chroma" ]; then
            echo "⚠️  Vector store missing at ./data/processed/chroma/"
            echo "    Run ingestion pipeline before using Chainlit for retrieval features."
        fi

        echo "Starting Chainlit UI on port 8000..."
        nohup chainlit run src/vira/ui/chainlit_app.py -w --port 8000 > "$CHAINLIT_LOG" 2>&1 &
        CHAINLIT_PID=$!
        sleep 3
        if ps -p $CHAINLIT_PID > /dev/null; then
            echo "✅ Chainlit started (PID: $CHAINLIT_PID)"
            echo "   Logs: tail -f $CHAINLIT_LOG"
        else
            echo "❌ Failed to start Chainlit. Check $CHAINLIT_LOG"
        fi
    fi
fi

printf '\n🎉 All requested services triggered.\n'
printf '   Backend:  http://localhost:8001\n'
printf '   Frontend: http://localhost:3000\n'
printf '   Chainlit: http://localhost:8000\n'
printf '\n'
