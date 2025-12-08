FROM public.ecr.aws/lambda/python:3.12

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml ${LAMBDA_TASK_ROOT}/
COPY uv.lock ${LAMBDA_TASK_ROOT}/
COPY README.md ${LAMBDA_TASK_ROOT}/

# Install dependencies using uv to system Python
RUN uv pip install --system --no-cache -r pyproject.toml

# Copy application code
COPY . ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler
CMD ["main.handler"]
