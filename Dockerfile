# =============================================================================
# Multi-Stage Dockerfile for 2GOI URL Shortener
# =============================================================================
#
# This Dockerfile builds both the React frontend and Python backend into
# a single container. This enables the single-domain architecture where
# everything (API, frontend, redirects) runs on one domain (2goi.in).
#
# Stage 1: Build the React frontend with Vite
# Stage 2: Set up the Python backend and copy the frontend build output
#
# The final image only contains the Python runtime + built frontend assets.
# Node.js is NOT included in the final image (multi-stage = smaller image).
# =============================================================================

# --------------- STAGE 1: Build React Frontend ---------------
FROM node:20-slim AS frontend-build
WORKDIR /frontend

# Vite embeds environment variables at BUILD TIME (not runtime).
# These must be set here so they end up in the compiled JavaScript bundle.
# VITE_API_URL is empty because frontend and backend are on the same domain.
# VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY are PUBLIC keys (safe to expose).
ENV VITE_API_URL=""
ENV VITE_SUPABASE_URL=https://svggdrykoxktgoimrqny.supabase.co
ENV VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN2Z2dkcnlrb3hrdGdvaW1ycW55Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM2NzY4NjIsImV4cCI6MjA4OTI1Mjg2Mn0.LEXeqEiUNgE16uselNYF54rbSLPBJ6qBF22j7c8Fdjo

# Install npm dependencies (uses package-lock.json for reproducible builds)
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source code and build the production bundle
COPY frontend/ .
RUN npm run build
# Output: /frontend/dist/ (contains index.html, JS bundles, CSS, assets)

# --------------- STAGE 2: Python Backend + Static Frontend ---------------
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies needed for psycopg2 (PostgreSQL driver)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ .

# Copy the built frontend from Stage 1 into the backend's static directory
# FastAPI serves these files directly (see main.py)
COPY --from=frontend-build /frontend/dist ./static

# Expose the application port
EXPOSE 8000

# Run with Gunicorn (process manager) + Uvicorn workers (async ASGI server)
# -w 4: 4 worker processes for handling concurrent requests
# --timeout 120: allow up to 2 minutes for long requests
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120", "--graceful-timeout", "30"]
