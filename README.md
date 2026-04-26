# Task Manager


[![Python CI](https://github.com/noahrv/python-project-52/actions/workflows/python-ci.yml/badge.svg)](https://github.com/noahrv/python-project-52/actions/workflows/python-ci.yml)

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=noahrv_python-project-52&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=noahrv_python-project-52)


### Hexlet tests and linter status:
[![Actions Status](https://github.com/noahrv/python-project-52/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/noahrv/python-project-52/actions)

## Демо

https://python-project-52-bcky.onrender.com


## Описание проекта

Task Manager — это веб-приложение для управления задачами.

Приложение позволяет создавать задачи, назначать исполнителей, менять статусы и группировать задачи с помощью меток.


## Возможности

- регистрация и аутентификация пользователей
- создание, редактирование и удаление пользователей
- создание, редактирование и удаление статусов задач
- создание, редактирование и удаление меток
- создание, редактирование, просмотр и удаление задач
- назначение исполнителя задачи
- привязка меток к задачам
- фильтрация задач по статусу, исполнителю, метке и автору
- защита удаления связанных сущностей
- отслеживание ошибок через Rollbar


## Установка

Склонируйте репозиторий и установите зависимости:
```bash
git clone https://github.com/noahrv/python-project-52.git
cd python-project-52
make install
```

## Настройка окружения

Создайте файл .env в корне проекта и добавьте переменные окружения:
```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/database
ROLLBAR_ACCESS_TOKEN=your-rollbar-token
```
Миграции
```
make migrate
```

## Запуск

Для запуска приложения в режиме разработки выполните:
```
uv run python manage.py runserver
```
Тесты
```
uv run python manage.py test
```