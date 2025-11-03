# Multi-stage build for LLM service
FROM python:3.12-slim as builder

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Set working directory
WORKDIR /app

# Copy dependency files
# Note: LLM service may use backend's pyproject.toml or have its own
# Adjust path based on your project structure
COPY backend/pyproject.toml backend/poetry.lock ./

# Configure Poetry to not create virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies (including LLM service specific ones)
RUN poetry install --no-interaction --no-ansi --no-root

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

# Copy LLM service code
COPY backend/llm-service/ ./llm-service/

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# Run the application
# Note: Adjust the path based on your actual module structure
CMD ["uvicorn", "llm-service.main:app", "--host", "0.0.0.0", "--port", "8000"]

