Запуск сервера:
1. Создать сервер на Linux (например, на reg.ru), и с помощью ssh подключиться к серверу в терминале.
2. Установить Postgres, pip, venv
3. Выполнить команду git clone https://github.com/NadinDesyatova/diploma_fpy_backend_version_1.git. 
4. Сделать настройки в settings.py, создать файл .env с корректными значениями:
SECRET_KEY=value
DEBUG=value
ALLOWED_HOSTS=value
DB_USER=value
DB_NAME=value
DB_PASSWORD=value
DB_HOST=value
DB_PORT=value
MEDIA_URL=value
MEDIA_ROOT_NAME=value
5. Активировать виртуальное окружение
6. Установить все зависимости (pip install -r requirements.txt)
7. Сделать миграции (предварительно установить и настроить БД при необходимости) (python manage.py migrate)
8. При использовании Nginx этот шаг нужно пропустить. Если не пользоваться Nginx и gunicorn, то можно запустить сервер командой python manage.py runserver 0.0.0.0:8000

Развертывание проекта с помощью Nginx и gunicorn:
1. Далее собрать статику (python manage.py collectstatic)
2. Установить gunicorn (если еще не установлен) (pip install gunicorn)
3. Запустить проект (DEBUG=False ... gunicorn my_proj.wsgi -b 0.0.0.0:8000)
4. Проверить доступность через браузер по адресу http://ip_вашего_сервера:8000 
5. Установить nginx (apt install nginx)
6. Сделать настройку nginx (файл /etc/nginx/sites-available/default)
7. Перезагрузить nginx (nginx -s reload)
8. Убедиться в доступности сайта по адресу http://ip_вашего_сервера 
