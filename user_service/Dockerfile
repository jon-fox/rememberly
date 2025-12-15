FROM public.ecr.aws/lambda/python:3.11

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set uv to use system Python
ENV UV_SYSTEM_PYTHON=1

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements and install dependencies using uv
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN uv pip install --no-cache -r requirements.txt

# Copy handler
COPY handler.py ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler
CMD ["handler.lambda_handler"]
