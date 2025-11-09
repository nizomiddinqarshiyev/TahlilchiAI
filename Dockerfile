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

# 5. Django loyihasini konteynerga nusxalash
COPY . .

# 7. Gunicorn orqali ishga tushirish
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
