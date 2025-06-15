# Multi-stage build for React frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production
COPY frontend/ ./
RUN npm run build

# Main Python container
FROM python:3.9-slim

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    libgstreamer1.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create necessary directories
RUN mkdir -p static/uploads static/results static/plates \
    && mkdir -p /tmp/EasyOCR \
    && chmod -R 777 /tmp/EasyOCR \
    && chmod -R 755 static \
    && chown -R root:root static

# Install Python dependencies including production server
COPY backend/requirements.txt ./
RUN pip install -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy config.py to both locations for flexibility
COPY backend/config.py ./config.py

COPY backend/model_security_checker.py ./backend/

# Copy built frontend
COPY --from=frontend-builder /app/frontend/build ./static/

# Debug: verify React files exist
RUN ls -la static/ && echo "=== React build files ===" && ls -la static/ | head -10

# Copy models and whitelist
COPY models/ ./models/
COPY backend/model_imports.whitelist ./backend/

# Verify critical files exist
RUN echo "=== Verifying files ===" && \
    ls -la models/ && \
    test -f models/best.pt && echo "✓ best.pt found" || echo "✗ best.pt missing" && \
    test -f backend/model_imports.whitelist && echo "✓ whitelist found" || echo "✗ whitelist missing"

# Set environment variables for HF Spaces
ENV FLASK_APP=backend/app.py
ENV FLASK_ENV=production
ENV YOLO_CONFIG_DIR=/tmp
ENV EASYOCR_MODULE_PATH=/tmp/EasyOCR
ENV PORT=7860

# Expose port 7860 (HF Spaces standard)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
  CMD curl -f http://localhost:7860/health || exit 1

# Run with Gunicorn production server
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "1", "--timeout", "120", "--max-requests", "100", "--preload", "backend.app:app"]