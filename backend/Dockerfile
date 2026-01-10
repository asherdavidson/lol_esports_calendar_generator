FROM debian:bookworm-slim

# Install uv via official docker image
COPY --from=ghcr.io/astral-sh/uv:0.9.24 /uv /uvx /bin/

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Create non-root user first
RUN useradd --create-home appuser

# Install Python and dependencies via uv
RUN uv sync --frozen --no-dev

# Copy application code
COPY backend/ ./backend/

# Fix permissions after all files are in place
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /app/.venv/bin/python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/leagues')" || exit 1

# Run with gunicorn
CMD ["uv", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend:app"]
