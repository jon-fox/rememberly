FROM public.ecr.aws/lambda/python:3.11

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set uv to use system Python
ENV UV_SYSTEM_PYTHON=1

COPY pyproject.toml ${LAMBDA_TASK_ROOT}/

# Install dependencies using uv (including uvicorn for ASGI server)
WORKDIR ${LAMBDA_TASK_ROOT}

RUN uv pip install --no-cache -r pyproject.toml uvicorn

# Copy handler
COPY . ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler
CMD ["handler.lambda_handler"]
