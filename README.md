# Дипломный проект по профессии «Fullstack-разработчик на Python»

## Облачное хранилище My Cloud (бэкенд на языке Python с использованием фреймворка Django и СУБД PostgreSQL, фронтенд на языках JavaScript, HTML, CSS с использованием библиотек React, React Router).

## Инструменты / ресурсы, которые потребуются для проекта:

- [PyCharm](https://www.jetbrains.com/ru-ru/pycharm/download) и/или [VS Code](https://code.visualstudio.com),
- [Python](https://www.python.org/),
- [Django](https://github.com/django/django),
- [Node.js](https://nodejs.org/),
- [React](https://reactjs.org/),
- [Git](https://git-scm.com/) + [GitHub](https://github.com/),
- [Reg.ru](https://www.reg.ru/).

## Для развертывания проекта необходимо выполнить следующие действия:

- Откройте на вашем компьютере терминал и сгенерируйте ssh ключ с помощью команды 
(по умолчанию ключ будет сохранён в домашней директории): 
`ssh-keygen`

- Либо можно добавить существующий ключ

- Вывести в терминал ssh ключ с помощью команды 
```
cat .ssh/название_вашего_ssh_файла.pub
```

- Скопировать публичный ключ 

- Заказать сервер с ОС Linux, например Ubuntu (добавив скопированный ssh), например на reg.ru https://cloud.reg.ru/

- Для того, чтобы подключиться к серверу, необходимо в терминале ввести команду 
```
ssh root@ip_созданного_сервера
```

- Ввести пароль доступа (приходит на почту, которая указана при регистрации на reg.ru)

- Создать вашего пользователя командой
`adduser user_name`
- Задать пароль дважды, в остальных полях можно нажимать Enter

- Добавить пользователя в группу sudo
`usermod user_name -aG sudo`

- Зайти под новым пользователем с помощью команды
`su user_name`

- Выполнить команду
`cd ~`

- Выполнить команды для обновления apt
```
sudo apt update
sudo apt upgrade
```

- Установить базовые программы:
`sudo apt install python3-venv python3-pip postgresql nginx`

- Установим Node.js через NodeSource, сначала добавим NodeSource репозиторий:
```
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
```

- Затем установим Node.js и npm:
```
sudo apt-get install -y nodejs
```

- Проверим, что установка прошла успешно:
```
node -v
npm -v
```
- Выполнить команду 
`sudo systemctl start nginx`

- Проверить статус nginx (должен быть active) с помощью команды
`sudo systemctl status nginx`

- Нажать `q` для выхода

- Скопироуйте репозиторий с проектом командой:
`git clone https://github.com/NadinDesyatova/diploma_project.git`

- Зайти в папку проекта:
`cd diploma_project`
```

- Создайте базу данных, выполнив последовательно команды:
```
sudo su postgres
psql
ALTER USER postgres WITH PASSWORD 'ваш_пароль';
CREATE DATABASE название_вашей_бызы_данных;
ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET timezone TO 'Europe/Moscow';
GRANT ALL PRIVILEGES ON DATABASE название_вашей_базы_данных TO postgres;
```

- Выполнить команды для выхода 
```
\q
exit
```

- Создать файл .env командой 
`nano .env`

- Задать в файле .env значения для переменных окружения для settings.py: 
```
SECRET_KEY=value # например, сгенерировать secret_key здесь: https://djecrety.ir/
DEBUG=True #
ALLOWED_HOSTS=value # перечислить через запятую, например localhost,127.0.0.1,ip_адрес_сервера
DB_USER=postgres
DB_NAME=value # название вашей базы данных
DB_PASSWORD=pass # пароль вашего пользователя postgres
DB_HOST=value # например, localhost
DB_PORT=5432 
MEDIA_URL=/media/ 
MEDIA_ROOT_NAME=media
```
- Чтобы сохранять изменения файлов в nano нужно выполнять команды:
`Ctrl + x` => `y` => `Enter`

- Перейдите в папку frontend:
`cd diploma_fpy_frontend`

- Выполните команду
```commandline
npm install
```

- Создайте в корне папки frontend файл .env:
```
nano .env
```

- Задайте значения для переменных в файле .env:
```
VITE_APP_BASE_URL_WEBSITE = http://your-server-ip-or-domain.com/ # адрес клиентского приложения
VITE_APP_BASE_USL_API = http://your-server-ip-or-domain.com/api/ # адрес api сервера
```

- Выполните команду:
```
npm run build
```

- Перейдите в папку backend:
```
cd ..
```

- Создайте и активируйте виртуальное окружение
```
python3 -m venv env
source env/bin/activate
```

- Установить зависимости
`pip install -r requirements.txt`

- Установить gunicorn
`pip install gunicorn`

- В файле app/signals.py задайте корректные значения для пользователя (login, name, password) с правами администратора, 
который будет создан в базе данных автоматически после проведения миграций
```
nano app/signals.py 
```

- Выполнить команду
`python manage.py migrate`

- Теперь можно сделать gunicorn сервисом в операционной системе, 
чтобы он был постоянно запущен и при старте сервера сам перезапускался, 
для этого нужно ввести команду для создания файла с настройками сервиса gunicorn
`sudo nano /etc/systemd/system/mycloud.service`

- Сохранить настройки сервиса в файле:
```
[Unit]
Description=My Cloud Gunicorn Daemon
After=network.target

[Service]
User=ваш_пользователь
Group=www-data
WorkingDirectory=/home/ваш_пользователь/diploma_project
ExecStart=/home/ваш_пользователь/diploma_project/env/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/ваш_пользователь/diploma_project/diploma_backend/project.sock diploma_backend.wsgi:application

[Install]
WantedBy=multi-user.target
```

- После создания юнита выполните:
```
sudo systemctl daemon-reload
sudo systemctl start mycloud
sudo systemctl enable mycloud
```

- Затем необходимо настроить файл конфигурации nginx. Команда для создания файла с настройками nginx:
`sudo nano /etc/nginx/sites-available/mycloud`
- Сохранить настройки Nginx в файле
```
server {
  listen 80;
  server_name your-server-ip-or-domain.com;

  location = /favicon.ico {
    access_log off;
    log_not_found off;
  }
    
  root /home/ваш_пользователь/diploma_project/diploma_fpy_frontend/dist; 
  index index.html index.htm;

  keepalive_timeout 5;

  location / {
    try_files $uri $uri/ /index.html;
  }

  location /media/ {
    root /home/ваш_пользователь/diploma_project;
  }

  location /api/ {
    proxy_pass http://unix:/home/ваш_пользователь/diploma_project/diploma_backend/project.sock;
  }
}
```
- Далее нужно создать симлинк и перезагрузить Nginx:
```
sudo ln -s /etc/nginx/sites-available/mycloud /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo ufw allow 'Nginx Full'
```

- При возникновении ошибки 502 Bad Gateway при развертывании с Nginx, убедитесь, 
что пользователь, от которого запущен Nginx (обычно www-data), имеет права на чтение/запись в директорию, где создается файл .sock.
- Проверить права можно с помощью команды:
`ls -l`
- Если права не установлены должным образом, можно добавить пользователя Nginx в группу, от которой создаётся файл .sock, 
— тогда доступ должен быть. 
- Для этого нужно использовать команду:
```
sudo usermod www-data -aG ваш_пользователь
```

## Рекомендации при внесении изменений в проект
- Если изменения внесены в код приложения Django, нужно перезапустить процесс сервера.
```
sudo systemctl restart mycloud
```
- Если изменения касаются конфигурации Nginx, необходимо проверить корректность синтаксиса конфига командой `sudo nginx -t` 
и, если ошибок нет, перезапустить Nginx: 
```
sudo systemctl restart nginx
```

### Чтобы открыть приложение, введите в адресной строке браузера: http://your-server-ip-or-domain.com/
