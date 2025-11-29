# 1. Asosiy image
FROM python:3.12-slim

# 2. Ishchi papka
WORKDIR /app

# 3. Tizim kutubxonalarini o‘rnatish
#RUN apt-get update && apt-get install -y \
#    libpq-dev gcc && \
#    rm -rf /var/lib/apt/lists/*

# 4. Kutubxonalarni o‘rnatish
COPY req.txt .
RUN pip install -r req.txt

RUN apt-get update && \
    apt-get install -y cron && \
    apt-get clean
# --- Add crontab file ---
COPY crontab /app/crontab/train_cron

# --- Give execution rights on the cron job ---
RUN chmod 0644 /app/crontab/train_cron

# --- Apply cron job ---
RUN crontab /ai/train


# --- Expose port if needed ---
EXPOSE 8000

# --- Run cron in foreground and also start Django server ---
CMD ["sh", "-c", "cron && tail -f /app/logs/train.log"]
# 5. Django loyihasini konteynerga nusxalash
COPY . .

# 7. Gunicorn orqali ishga tushirish
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
