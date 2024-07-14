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
git clone https://github.com/VladiFinogenov/DRF-myblog.git
```

## Шаг 2: Переход в директорию проекта

```bash
cd DRF-myblog
```

## Шаг 3: Настройка переменных окружения

`Создайте файл .env в корневой директории проекта и добавьте в него необходимые переменные окружения. Для этого скопируйте и заполните из empty_env переменные. Пример:`
```bash
DEBUG = True
SECRET_KEY = 'django-insecure-xxxxxxxxxxxx'
DJANGO_ALLOWED_HOSTS = '127.0.0.1'
CSRF_TRUSTED_ORIGINS = 'http://127.0.0.1'
INTERNAL_IPS = '127.0.0.1'

POSTGRES_USER = 'blog'
POSTGRES_PASSWORD = 'new_password'
POSTGRES_DB = 'your_database'
```
## Шаг 4: Сборка и запуск контейнеров Docker

`Соберите и запустите контейнеры Docker с помощью docker-compose:`
```bash
docker compose up --build
```
`Эта команда соберет образы Docker и запустит контейнеры в соответствии с конфигурацией, указанной в файле docker-compose.yml.`

## Шаг 5: Создание миграций

`Создайте миграции с помошью команд:`
```bash
docker compose run web python manage.py makemigrations
```
```bash
docker compose run web python manage.py migrate
```

## Шаг 6: Сборка статики

`Загрузите статику с помошью команды:`
```bash
docker compose run web python manage.py collectstatic --noinput
```

## Шаг 7: Создание суперпользователя

`Создайте суперпользователя для доступа к административной панели:`
`Для этого откройте второй терминал и введите команду:`
```bash
docker compose run web python manage.py createsuperuser
```

# Запуск тестов

`Запустите проект через docker compose см. шаг 4, откройте второй терминал и введите команду`

```bash
docker compose run web python manage.py test
```