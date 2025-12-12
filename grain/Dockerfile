# Use the official TensorFlow GPU image as the base
FROM tensorflow/tensorflow:latest-gpu

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    scipy \
    matplotlib \
    pandas \
    scikit-learn \
    joblib \
    Pillow \
    tqdm \
    scikit-image 

RUN pip install --no-cache-dir \
    fastapi[all] \
    uvicorn[standard] \
    python-multipart \
    loguru

WORKDIR /app
COPY src/ ./src/

RUN mkdir -p /app/logs
ENV PYTHONPATH=/app/src

EXPOSE 80

ENTRYPOINT ["python", "src/main.py"]