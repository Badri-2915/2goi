# Stage 1: Build frontend
FROM node:20-slim AS frontend-build
WORKDIR /frontend

# Frontend env vars must be available at build time (Vite embeds them)
# These are PUBLIC keys (anon key is designed to be exposed in frontend code)
ENV VITE_API_URL=""
ENV VITE_SUPABASE_URL=https://svggdrykoxktgoimrqny.supabase.co
ENV VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN2Z2dkcnlrb3hrdGdvaW1ycW55Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM2NzY4NjIsImV4cCI6MjA4OTI1Mjg2Mn0.LEXeqEiUNgE16uselNYF54rbSLPBJ6qBF22j7c8Fdjo

COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: Python backend + frontend static files
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ .

# Copy frontend build into backend static directory
COPY --from=frontend-build /frontend/dist ./static

# Expose port
EXPOSE 8000

# Run with gunicorn + uvicorn workers for production
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120", "--graceful-timeout", "30"]
