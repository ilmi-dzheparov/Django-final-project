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
cd teamproject_41
```

## Шаг 3: Настройка переменных окружения

`Создайте файл .env.docker в корневой директории проекта и добавьте в него необходимые переменные окружения. Пример:`
```bash
DB_HOST = 'db'
DB_PORT = '5432'
DB_NAME = meganodatabase
DB_USER = megano
DB_PASS = pass_megano
```
## Шаг 4: Сборка и запуск контейнеров Docker

`Соберите и запустите контейнеры Docker с помощью docker-compose:`
```bash
sudo docker compose up --build
```
`Эта команда соберет образы Docker и запустит контейнеры в соответствии с конфигурацией, указанной в файле docker-compose.yml.`

## Шаг 5: Создание миграций

`Создайте миграции с помошью команды:`
```bash
sudo docker compose run web python manage.py migrate
```

## Шаг 6: Сборка статики

`Загрузите статику с помошью команды:`
```bash
sudo docker compose run web python manage.py collectstatic --noinput
```

## Шаг 7: Создание суперпользователя

`Создайте суперпользователя для доступа к административной панели:`
```bash
sudo docker compose run web python manage.py createsuperuser
```

# Загрузка фикстур

* `!!! Загружайте фикстуры только после создания суперпользователя`
* `!!! Добавляйте других пользователей только после загрузки фикстур`
`Загрузите фикстуры с помошью команды:`
```bash
sudo docker compose run web python manage.py loaddata fixtures/full-data.json
```