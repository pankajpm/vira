#!/bin/bash
# Start both backend and frontend services for VIRA

cd "$(dirname "$0")"
source .venv/bin/activate

echo "Starting backend API on port 8000..."
uvicorn vira.backend.api:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Waiting for backend to start..."
sleep 3

echo "Starting Streamlit UI on port 8501..."
python -m streamlit run src/vira/ui/app.py &
STREAMLIT_PID=$!

echo ""
echo "✅ Services started successfully!"
echo "   Backend API: http://localhost:8000"
echo "   Frontend UI: http://localhost:8501"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Streamlit PID: $STREAMLIT_PID"
echo ""
echo "To stop services, run: kill $BACKEND_PID $STREAMLIT_PID"

