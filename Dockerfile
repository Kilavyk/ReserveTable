FROM python:3.13.2
WORKDIR /code

# Установка системных зависимостей
RUN apt-get update && apt-get install -y gcc libpq-dev postgresql-client && rm -rf /var/lib/apt/lists/*

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Создаём директории для статики и медиа
RUN mkdir -p /code/static /code/media

# Копируем исходный код
COPY . .

# Открываем порт
EXPOSE 8000

# Команда будет указана в docker-compose
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
