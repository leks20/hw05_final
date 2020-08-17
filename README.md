# Yatube

Интернет-блог, написанный на Python с помощью веб-фреймворка Django

В Yatube можно создавать посты с фотографиями, комментировать записи и подписываться на других авторов

Пример работы проекта на https://blog-yatube.tk

## Как запустить проект:

1) Клонируйте репозитроий с программой:
```
git clone https://github.com/leks20/yatube
```
2) В созданной директории установите виртуальное окружение, активируйте его и установите необходимые зависимости:
```
python3 -m venv venv

. venv/bin/activate

pip install -r requirements.txt
```
3) Создайте в директории файл .env и поместите туда SECRET_KEY, необходимый для запуска проекта

4) Выполните миграции:
```
python manage.py migrate
```
5) Создайте суперпользователя:
```
python manage.py createsuperuser
```
6) Запустите сервер:
```
python manage.py runserver
```
____________________________________

Ваш проект запустился на http://127.0.0.1:8000/

С помощью команды *pytest* вы можете запустить тесты и проверить работу модулей

Для подтверждения регистрации и сброса пароля используйте папку *sent_emails*







