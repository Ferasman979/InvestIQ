# Multi-stage build for LLM service
FROM python:3.12-slim as builder

# Set working directory
WORKDIR /app

# Copy dependency files
# LLM service uses the same dependencies as backend
COPY backend/pyproject.toml ./

# Install build dependencies
RUN pip install --no-cache-dir build

# Install dependencies using pip (project uses PEP 621 format, not Poetry)
RUN pip install --no-cache-dir \
    fastapi>=0.120.4 \
    "uvicorn[standard]>=0.38.0" \
    pyjwt>=2.10.1 \
    python-dotenv>=1.2.1 \
    python-multipart>=0.0.20 \
    sqlalchemy>=2.0.44 \
    psycopg2-binary>=2.0.9 \
    langchain-google-genai \
    python-dateutil

# Production stage
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Install any additional dependencies needed for LLM service
RUN pip install --no-cache-dir langchain-google-genai python-dateutil

# Copy LLM service code (need to copy the whole backend to maintain imports)
COPY backend/ ./backend/

# Set Python path so imports work
ENV PYTHONPATH=/app

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# Run the application
# Change to backend/llm-service directory and run from there
WORKDIR /app/backend/llm-service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

