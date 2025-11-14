FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и устанавливаем Python зависимости
COPY bot/src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY bot/src/ .

# Копируем статические файлы
COPY bot/static/ /app/static/

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["python", "run.py"]