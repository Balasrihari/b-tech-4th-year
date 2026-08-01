# Multi-stage Dockerfile for AI-Powered Smart Student Learning Assistant

# Stage 1: Backend
FROM python:3.11-slim as backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Expose backend port
EXPOSE 8000

# Run backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Stage 2: Frontend
FROM node:18-alpine as frontend

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend code
COPY frontend/ .

# Build frontend
RUN npm run build

# Expose frontend port
EXPOSE 5173

# Run frontend in development mode
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Stage 3: Production (Combined)
FROM node:18-alpine as production

WORKDIR /app

# Copy built frontend
COPY --from=frontend /app/dist ./frontend/dist

# Copy backend
COPY --from=backend /app ./backend

# Install nginx for serving static files
RUN apk add --no-cache nginx

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
