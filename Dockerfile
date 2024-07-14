FROM python:3.11

# Устанавливаем переменные окружения
ENV DJANGO_SETTINGS_MODULE=megano.settings
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы requirements.txt в контейнер
COPY requirements.txt /app/

# Устанавливаем зависимости Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем весь проект в контейнер
COPY src . /app/

# Указываем, что контейнер будет слушать на порту 8000
EXPOSE 8000

CMD ['gunicorn', 'megano.wsgi:application', '--bind', '0.0.0.0:8000']
