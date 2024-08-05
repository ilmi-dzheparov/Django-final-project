# TeamProject_41



## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/ee/gitlab-basics/add-file.html#add-a-file-using-the-command-line) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.skillbox.ru/pythondjango_team41/teamproject_41.git
git branch -M master
git push -uf origin master
```

## Шаг 1: Клонирование репозитория

`Сначала клонируйте репозиторий на ваш локальный компьютер. Для этого выполните следующую команду:`

```bash
git clone https://gitlab.skillbox.ru/pythondjango_team41/teamproject_41.git
```

## Шаг 2: Переход в директорию проекта

```bash
cd teamproject_41
```

## Шаг 3: Настройка переменных окружения

`Создайте файл .env в корневой директории проекта и добавьте в него необходимые переменные окружения:`
```
DEBUG = True
DJANGO_SECRET_KEY = 'django-insecure-xxxxxxxxxxxx'
DJANGO_ALLOWED_HOSTS = *

DB_ENGINE = "django.db.backends.postgresql"  # замените это значение если хотите использовать SQlite3 'django.db.backends.sqlite3'
DB_HOST = 'db'
DB_PORT = '5433'
DB_NAME = megano
DB_USER = megano
DB_PASS = user1234!

DATABASE = postgress  # при использовании PostgreSQL

CACHES_BACKEND = "django_redis.cache.RedisCache",
CACHES_LOCATION = 'redis://redis:6379/1',

EMAIL_HOST='smtp.yandex.ru'
EMAIL_PORT=465
EMAIL_HOST_USER='example@email.com'
EMAIL_HOST_PASSWORD='you_password'
DOMEN_APP='http://127.0.0.1:8000'

STRIPE_PUBLISHABLE_KEY = '' # добавьте свой публичный ключ от сервиса
STRIPE_SECRET_KEY = '' # добавьте свой приватный ключ от сервиса
```
`Для отправки писем со ссылкой на изменение пароля необходимо заполнить значения EMAIL. Также необходимо заменить при
необходимости значения EMAIL_USE_TLS и EMAIL_USE_SSL в settings.py.
В DOMEN_APP необходимо ввести фактический домен вашего приложения.`
`Ознакомление с ними выходит за рамки данной инструкции, но с подробностями можно ознакомиться
здесь:` https://ilyakhasanov.ru/baza-znanij/prochee/nuzhno-znat/139-nastrojki-otpravki-pochty-cherez-smtp.
`Стоит учитывать, что не все почтовые ящики дают заполнять в качестве пароля, большинство (яндекс, гугл и т.д.)
генерируют пароль самостоятельно. Для ознакомления с особенностями подключения smtp обращайтесь
к документации почтового сервиса.`
## Шаг 4: Сборка и запуск контейнеров Docker

`Соберите и запустите контейнеры Docker с помощью docker-compose:`
```bash
docker compose -f docker-compose.yml up -d --build
```
`Эта команда соберет образы Docker и запустит контейнеры в соответствии с конфигурацией, указанной в файле docker-compose.yml.`

## Шаг 5: Создание миграций

`Создайте миграции с помошью команды:`
```bash
docker compose -f docker-compose.yml exec web python manage.py makemigrations --no-input
```
```bash
docker compose -f docker-compose.yml exec web python manage.py migrate --no-input
```

## Шаг 6: Сборка статики

`Загрузите статику с помошью команды:`
```bash
docker compose -f docker-compose.yml exec web python manage.py collectstatic --no-input
```

## Шаг 7: Создание суперпользователя

`Создайте суперпользователя для доступа к административной панели:`
```bash
docker compose -f docker-compose.yml exec web python manage.py createsuperuser
```

# Загрузка фикстур

* `!!! Загружайте фикстуры только после создания суперпользователя`
* `!!! Добавляйте других пользователей только после загрузки фикстур`
`Загрузите фикстуры с помошью команды:`
```bash
docker compose -f docker-compose.yml exec web python manage.py loaddata fixtures/full-data.json
```
