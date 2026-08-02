#!/bin/bash

echo "========================================"
echo "AI Student Learning Assistant"
echo "========================================"
echo ""
echo "Starting Backend Server..."
cd backend
gnome-terminal -- bash -c "venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000; exec bash" &
echo "Backend server starting on http://localhost:8000"
echo ""
echo "Starting Frontend Server..."
cd ../frontend
gnome-terminal -- bash -c "npm run dev; exec bash" &
echo "Frontend server starting on http://localhost:5173"
echo ""
echo "========================================"
echo "Application is starting..."
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
echo ""
