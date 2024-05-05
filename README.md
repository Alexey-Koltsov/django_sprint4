# Проект «Блогикум»

Блогикум - сайт, на котором пользователь может создать свою страницу и публиковать на ней сообщения («посты»). 
Для каждого поста нужно указать категорию — например «путешествия», «кулинария» или «python-разработка», а также опционально локацию, с которой связан пост, например «Остров отчаянья» или «Караганда». 
Пользователь может перейти на страницу любой категории и увидеть все посты, которые к ней относятся.
Пользователи смогут заходить на чужие страницы, читать и комментировать чужие посты.

# Стек использованных технологий

- Python3
- Django Framework
- Django Template Language
- Django Bootstrap5
- SQLite3

## Как запустить проект:

## Клонировать репозиторий и перейти в него в командной строке
`
git clone git@github.com:Alexey-Koltsov/django_sprint4.git
`

`
сd django_sprint4
`
## Cоздать виртуальное окружение
Windows
`
python -m venv venv
`

LinuxmacOS
`
python3 -m venv venv
`

## Активировать виртуальное окружение
Windows
`
source venv/Scripts/activate
`

LinuxmacOS
`
source venv/bin/activate
`
## Обновить PIP

Windows
`
python -m pip install --upgrade pip
`

LinuxmacOS
`
python3 -m pip install --upgrade pip
`

## Установить зависимости из файла requirements.txt
`
pip install -r requirements.txt
`
## Установить зависимости из файла requirements.txt
`
pip install -r requirements.txt
`

## Перейти в папку blogicum
`
сd blogicum
`
## Выполнить миграции

Windows
`
python manage.py makemigrations
`
python manage.py migrate
`

LinuxmacOS
`
python3 manage.py makemigrations
`
`
python3 manage.py migrate
`

## Фикстуры
В репозитории проекта есть файл с дампом базы данных: db.json. Дамп содержит несколько постов; вы можете загрузить его в базу и посмотреть, как выглядит и работает наполненный сайт.

Windows
`
python manage.py loaddata db.json
`

LinuxmacOS
`
python3 manage.py loaddata db.json
`


## Запустить проект
Windows
`
python manage.py runserver
`

LinuxmacOS
`
python3 manage.py runserver
`

## Автор: 
Кольцов Алексей.