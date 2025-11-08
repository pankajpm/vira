#!/bin/bash
# Start both FastAPI backend and React frontend

echo "🚀 Starting VIRA React Stack..."
echo ""

# Kill any existing processes
echo "Cleaning up old processes..."
pkill -f "uvicorn vira.backend.api"
pkill -f "react-scripts start"
sleep 2

# Start FastAPI backend on port 8001
echo "Starting FastAPI backend on port 8001..."
cd /Users/pankaj/projects/vira
source .venv/bin/activate
nohup uvicorn vira.backend.api:app --reload --host 0.0.0.0 --port 8001 > /tmp/vira-backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"
echo "   Logs: tail -f /tmp/vira-backend.log"
echo ""

# Wait for backend to start
sleep 3

# Start React frontend on port 3000
echo "Starting React frontend on port 3000..."
cd /Users/pankaj/projects/vira/frontend
nohup npm start > /tmp/vira-frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo "   Logs: tail -f /tmp/vira-frontend.log"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 VIRA React Stack Running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Backend API:  http://localhost:8001"
echo "🌐 Frontend UI:  http://localhost:3000"
echo ""
echo "📚 API Docs:     http://localhost:8001/docs"
echo "🔍 Health Check: http://localhost:8001/health"
echo ""
echo "To stop:"
echo "  pkill -f 'uvicorn vira.backend.api'"
echo "  pkill -f 'react-scripts start'"
echo ""

# Wait a bit and check if services are running
sleep 5

echo "Checking services..."
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend not responding"
fi

if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running"
else
    echo "⏳ Frontend still starting (may take 30-60 seconds)..."
fi

echo ""
echo "Open http://localhost:3000 in your browser!"

