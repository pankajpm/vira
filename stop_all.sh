#!/bin/bash
# Stop all VIRA services (backend, React frontend, Chainlit UI)

set -u

printf '\n🛑 Stopping all VIRA services...\n\n'

STATUS=0

stop_process() {
    local pattern="$1"
    local name="$2"

    if pgrep -f "$pattern" > /dev/null 2>&1; then
        if pkill -f "$pattern" > /dev/null 2>&1; then
            echo "✅ Stopped $name"
        else
            echo "❌ Failed to stop $name" >&2
            STATUS=1
        fi
    else
        echo "ℹ️  $name not running"
    fi
}

stop_process "chainlit run src/vira/ui/chainlit_app.py" "Chainlit UI"
stop_process "react-scripts start" "React frontend"
stop_process "npm start" "React npm wrapper"
stop_process "uvicorn vira.backend.api" "FastAPI backend"
stop_process "streamlit run src/vira/ui/app.py" "Streamlit UI"

printf '\n✔️  Shutdown complete.\n\n'

exit $STATUS
