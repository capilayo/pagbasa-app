# ── Base image: official Python 3.11 slim (public, no auth needed) ────────────
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1001 appuser

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER 1001

# Expose default port (Render/Railway override via PORT env var)
EXPOSE 8080

# Start gunicorn — respects $PORT for Render/Railway/Code Engine
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --timeout 120 app:app"]
