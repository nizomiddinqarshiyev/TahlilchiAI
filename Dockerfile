# 1. Asosiy image
FROM python:3.12-slim

# 2. Ishchi papka
WORKDIR /app

# 3. Tizim kutubxonalarini o‘rnatish
RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# 4. Kutubxonalarni o‘rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Django loyihasini konteynerga nusxalash
COPY . .

# 6. Django’ni run qilish
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
