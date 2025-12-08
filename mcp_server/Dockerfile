FROM public.ecr.aws/lambda/python:3.12

# Copy project files
COPY pyproject.toml ${LAMBDA_TASK_ROOT}/
COPY README.md ${LAMBDA_TASK_ROOT}/

# Install dependencies with platform-specific wheels for Lambda (x86_64)
RUN pip install --no-cache-dir \
    --platform manylinux2014_x86_64 \
    --only-binary=:all: \
    --target ${LAMBDA_TASK_ROOT} \
    --implementation cp \
    --python-version 3.12 \
    anysqlite>=0.0.5 fastmcp>=2.13.0.2 httpx>=0.28.1 pandas>=2.3.3

# Copy application code
COPY . ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler
CMD ["main.handler"]
