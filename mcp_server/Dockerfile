FROM public.ecr.aws/lambda/python:3.12

# Install AWS Lambda Web Adapter
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.9.1 /lambda-adapter /opt/extensions/lambda-adapter

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set uv to use system Python
ENV UV_SYSTEM_PYTHON=1

# Copy project files
COPY pyproject.toml ${LAMBDA_TASK_ROOT}/
COPY README.md ${LAMBDA_TASK_ROOT}/

# Install dependencies using uv (including uvicorn for ASGI server)
WORKDIR ${LAMBDA_TASK_ROOT}
RUN uv pip install --no-cache -r pyproject.toml uvicorn

# Copy application code
COPY . ${LAMBDA_TASK_ROOT}/

# Configure Lambda Web Adapter
ENV PORT=8080
ENV AWS_LWA_READINESS_CHECK_PATH=/

# Set HOME to /tmp for Lambda (only writable directory)
# This prevents FastMCP from trying to create directories in non-writable locations
ENV HOME=/tmp

# Override the Lambda entrypoint to run our web app directly
ENTRYPOINT []

# Start uvicorn directly with server:app - Lambda Web Adapter handles the rest
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
