FROM public.ecr.aws/lambda/python:3.12

# Copy application code
COPY index.py ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler
CMD ["index.handler"]
