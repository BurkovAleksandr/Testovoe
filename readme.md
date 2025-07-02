# 🧾 SUIP Metadata Parser

FastAPI-приложение для извлечения и хранения метаданных файлов через сервис [suip.biz](https://suip.biz/ru/?act=mat).

## 🚀 Возможности

- 📤 Загрузка файла и извлечение метаданных с suip.biz
- 💾 Сохранение результатов в PostgreSQL
- 📥 Скачивание JSON-отчётов по каждой записи
- 🔎 REST API с фильтрацией и пагинацией

---

## ⚙️ Запуск с Docker

```bash
git clone https://github.com/yourname/suip-parser-api.git
cd suip-parser-api
docker-compose up --build
```

Приложение будет доступно по адресу: `http://localhost:8000`

Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 API Эндпоинты

### `POST /suip-data/parse`

Загрузка и парсинг файла

```bash
curl -X POST http://localhost:8000/suip-data/parse \
     -F "file=@example.jpg"
```

### `GET /suip-data`

Получить сохранённые результаты с фильтрацией и пагинацией

Параметры:

- `filename`: фильтрация по части имени файла
- `limit`: кол-во записей (по умолчанию 10)
- `offset`: сдвиг (по умолчанию 0)

```bash
curl "http://localhost:8000/suip-data?filename=pdf&limit=5&offset=0"
```

### `GET /suip-data/{id}/report`

Скачать отчёт по конкретной записи в формате `.json`

Пример:

```
http://localhost:8000/suip-data/3/report
```

---

## 🐘 База данных

Настройки PostgreSQL (см. `.env` или `docker-compose.yml`):

```
host: db
port: 5432
user: postgres
password: postgres
dbname: suip
```

---

## 📂 Структура проекта

```
├── main.py               # API логика
├── parser.py             # Логика парсера
├── Dockerfile            # Docker образ FastAPI
├── docker-compose.yml    # Сборка backend + PostgreSQL
├── README.md             # Инструкция
```
