# Extends official Ultralytics Docker image for YOLO11
FROM ultralytics/ultralytics:latest-cpu

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install FastAPI and dependencies
RUN uv pip install fastapi[all] uvicorn[standard] loguru --system

WORKDIR /app
COPY src/ ./src/
COPY pyproject.toml ./

# Install the application package
RUN uv pip install -e . --system

RUN mkdir -p /app/logs
ENV PYTHONPATH=/app/src

EXPOSE 80

# Start the inference server
ENTRYPOINT ["python", "src/main.py"]