# Backend mit Stockfish und optionaler Figurenerkennung (YOLO, CPU-PyTorch).
# Modell nicht im Image: chess_yolov8n.pt nach /app/chess_yolov8n.pt einbinden.
# Partien liegen in /data (BRETT_DATA_DIR), als Volume einbinden.
FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends stockfish libgl1 libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# CPU-Build von PyTorch zuerst, sonst zieht ultralytics die mehrere GB große CUDA-Variante
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend.py vision_engine.py games_store.py ./
COPY static ./static

ENV BRETT_DATA_DIR=/data \
    YOLO_CONFIG_DIR=/tmp/ultralytics \
    PYTHONUNBUFFERED=1
VOLUME /data
EXPOSE 8000
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]
