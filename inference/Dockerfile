FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
COPY inference/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY inference /app/inference
COPY models/model_best.pth /app/models/model_best.pth
ENV MODEL_PATH=/app/models/model_best.pth
EXPOSE 8000
CMD ["uvicorn", "inference.app:app", "--host", "0.0.0.0", "--port", "8000"]

