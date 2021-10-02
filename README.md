# BehaviorWatcher

## Структура проекта

* ```/dist``` + ```index.html``` - для просмотра swagger на github pages
* ```/backend``` - независимый сервер для работы BehaviorWatcher
* ```/frontend``` - независимый сервер для проверки работы скрипта, который собирает статистику и отправляет на сервер

## Развёртывание

### С использованием Docker

1. Ставим на Вашу ОС [Docker](https://www.docker.com/) и [docker-compose](https://docs.docker.com/compose/)
2. Запускаем контейнеры: ``` $ docker-compose up --build -d```
3. Проверяем их статус: ``` $ docker-compose ps```

### Ручное

*Следуем инструкции по развертыванию для каждого отдельного сервиса*
