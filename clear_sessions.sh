#!/bin/bash
# Clear all VIRA sessions
# Usage: ./clear_sessions.sh [--confirm]

cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the clear sessions script
python scripts/clear_sessions.py "$@"

