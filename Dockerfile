FROM python:3.12-slim

# Tizim paketlari (ffmpeg audio konvertatsiya uchun)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Kutubxonalarni o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha kodlarini ko'chirish
COPY . .

# Loglar va temp papkalarini yaratish
RUN mkdir -p logs temp

CMD ["python", "run.py"]
