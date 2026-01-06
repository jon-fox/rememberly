FROM public.ecr.aws/docker/library/python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml README.md ./

# Install dependencies using uv (including uvicorn for ASGI server)
RUN uv pip install --system --no-cache -r pyproject.toml uvicorn

# Copy application code
COPY . .

# Configure application
ENV PORT=8080

# Start uvicorn directly
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]

