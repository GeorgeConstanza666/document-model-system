# Програмна система для створення документної моделі організації проєкту

Дипломний проєкт. Реалізація модуля документів на основі статті:  
**Кунгурцев А. Б., Чорба А. І. (2025). «Терм-словникова технологія відбору виконавців задач у проєктах розробки програмного забезпечення».**

---

## Модель документа (формула 3)

```
Doc = ⟨idD, sAuthor, SubjArea, Date, sDocTerm, sTechnology⟩
```

| Поле | Тип | Опис |
|------|-----|------|
| `idD` | int | Ідентифікатор документа |
| `sAuthor` | множина | Автори з внесками (сума = 100%) |
| `SubjArea` | string | Предметна область / домен |
| `Date` | date | Дата створення |
| `sDocTerm` | множина | Терміни з `qTerm` та `relFreqTerm` |
| `sTechnology` | множина | Технології зі `degreeOfUseTech` |

### Формули

| Формула | Визначення |
|---------|------------|
| `qTerm` | Кількість входжень терміну в текст (ціле слово, без урахування регістру) |
| `relFreqTerm` | `round(qTerm / total_words × 100, 4)` |
| `degreeOfUseTech` | `min(100.0, mention_count × 10.0)` |

---

## Архітектура системи

```
┌─────────────────────────────────────────────────────────────┐
│                        Браузер                              │
│                                                             │
│   React 18 + Vite + TailwindCSS                             │
│   ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│   │  Завантаж.  │  │  Документи   │  │  Спеціалісти /   │  │
│   │  (Wizard)   │  │  (список +   │  │  Словники        │  │
│   │  3 кроки    │  │   деталі)    │  │  (список + дет.) │  │
│   └──────┬──────┘  └──────┬───────┘  └────────┬─────────┘  │
│          └────────────────┼──────────────────-┘            │
│                     axios (REST)                            │
└───────────────────────────┼─────────────────────────────────┘
                            │ HTTP / JSON
┌───────────────────────────┼─────────────────────────────────┐
│                     FastAPI (port 8000)                     │
│                                                             │
│   /api/documents          /api/specialists                  │
│   /api/domains            /api/dictionaries                 │
│   /api/authors                                              │
│                                                             │
│   ┌──────────────────────────────────────────────────────┐  │
│   │              DocumentProcessor                       │  │
│   │  FileParser → LangDetect → Translator → KeyBERT NLP  │  │
│   └──────────────────────────────────────────────────────┘  │
│                                                             │
│   ┌──────────────────────────────────────────────────────┐  │
│   │               SQLAlchemy ORM                         │  │
│   └──────────────────────┬───────────────────────────────┘  │
└──────────────────────────┼──────────────────────────────────┘
                           │
                    SQLite (app.db)
```

### Схема бази даних

```
domains ──< documents ──< document_terms >── terms
   │                  └─< document_technologies >── technologies
   │                  └─< author_contributions >── authors
   │                                                    │
   └──< dictionaries ──< dictionary_entries >── terms   │
                                                        │
                                               specialists(author_id)
```

---

## Стек технологій

| Шар | Технологія |
|-----|-----------|
| Backend | Python 3.11+, FastAPI 0.110, SQLAlchemy 2.0, SQLite |
| Валідація | Pydantic v2 |
| NLP | KeyBERT (`all-MiniLM-L6-v2`), spaCy |
| Переклад | deep-translator (Google Translate API) |
| Детекція мови | langdetect |
| Парсинг файлів | python-docx (.docx), pdfplumber (.pdf), вбудований (.txt) |
| Frontend | React 18, Vite, TailwindCSS, React Query, React Router, axios |
| Сповіщення | react-hot-toast |
| Тестування | pytest, FastAPI TestClient |

---

## Структура проєкту

```
Software system for creating a project organization document model/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── authors.py
│   │   │       ├── dictionaries.py
│   │   │       ├── documents.py
│   │   │       ├── domains.py
│   │   │       └── specialists.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── author.py
│   │   │   ├── document.py
│   │   │   ├── domain.py
│   │   │   ├── technology.py
│   │   │   └── term.py
│   │   ├── schemas/
│   │   │   ├── document.py
│   │   │   ├── requests.py
│   │   │   └── responses.py
│   │   ├── services/
│   │   │   ├── document_processor.py
│   │   │   ├── file_parser/
│   │   │   ├── nlp/
│   │   │   └── translation/
│   │   └── main.py
│   ├── scripts/
│   │   └── seed.py           # 5 тестових документів
│   ├── tests/
│   │   ├── test_api_endpoints.py   # 16 інтеграційних тестів
│   │   └── test_calculations.py    # 18 юніт-тестів формул
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ErrorBoundary.jsx
│   │   │   └── Layout.jsx
│   │   ├── pages/
│   │   │   ├── DictionariesPage.jsx
│   │   │   ├── DictionaryDetailsPage.jsx
│   │   │   ├── DocumentDetailsPage.jsx
│   │   │   ├── DocumentsListPage.jsx
│   │   │   ├── SpecialistDetailsPage.jsx
│   │   │   ├── SpecialistsPage.jsx
│   │   │   └── UploadDocumentPage.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── queryClient.js
│   │   └── App.jsx
│   ├── index.html
│   └── package.json
├── .gitignore
├── CLAUDE.md
└── README.md
```

---

## Встановлення та запуск

### Передумови

- Python 3.11+
- Node.js 18+

### Backend

```bash
cd backend

# Створити та активувати віртуальне середовище
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

# Встановити залежності
pip install -r requirements.txt

# Завантажити мовну модель spaCy (якщо ще не встановлена)
python -m spacy download en_core_web_sm

# Запустити сервер розробки
uvicorn app.main:app --reload
```

Сервер доступний за адресою: **http://localhost:8000**  
Swagger UI (документація API): **http://localhost:8000/docs**

#### Заповнити БД тестовими даними (опційно)

```bash
# з директорії backend/
python scripts/seed.py
```

Додає 5 документів у доменах: Машинне навчання, Веб-розробка, DevOps, Кібербезпека, Мобільна розробка.

### Frontend

```bash
cd frontend

# Встановити залежності
npm install

# Запустити сервер розробки
npm run dev
```

Фронтенд доступний за адресою: **http://localhost:5173**

---

## Тестування

```bash
cd backend

# Всі тести (без NLP/мережевих викликів)
pytest -m "not network" -v

# Лише юніт-тести формул
pytest tests/test_calculations.py -v

# Лише API-інтеграційні тести
pytest tests/test_api_endpoints.py -v
```

Тести використовують in-memory SQLite (`StaticPool`) та мокують `DocumentProcessor`.  
Мережевих залежностей (Google Translate, KeyBERT download) немає.

---

## API Reference

### Документи

| Метод | URL | Опис |
|-------|-----|------|
| `POST` | `/api/documents/upload` | Завантажити файл (.docx/.pdf/.txt), отримати чернетку |
| `POST` | `/api/documents/{draft_id}/finalize` | Зберегти чернетку з авторами та доменом |
| `GET` | `/api/documents` | Список документів (пагінація: `page`, `page_size`) |
| `GET` | `/api/documents/{id}` | Деталі документа |
| `DELETE` | `/api/documents/{id}` | Видалити документ |

### Домени / Автори

| Метод | URL | Опис |
|-------|-----|------|
| `GET` | `/api/domains` | Список предметних областей |
| `POST` | `/api/domains` | Створити домен |
| `GET` | `/api/authors` | Список авторів |

### Спеціалісти / Словники

| Метод | URL | Опис |
|-------|-----|------|
| `GET` | `/api/specialists` | Список спеціалістів із кількістю документів і термінів |
| `GET` | `/api/specialists/{id}` | Деталі спеціаліста |
| `GET` | `/api/dictionaries` | Список словників (по одному на домен) |
| `GET` | `/api/dictionaries/{id}` | Терміни словника, відсортовані за частотою |

### Приклад: завантаження та збереження документа

```bash
# Крок 1: завантажити файл
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@report.docx"
# → { "draft_id": "abc-123", "processed": { ... } }

# Крок 2: зберегти з авторами та доменом
curl -X POST http://localhost:8000/api/documents/abc-123/finalize \
  -H "Content-Type: application/json" \
  -d '{
    "domain_name": "Машинне навчання",
    "authors": [{"full_name": "Іван Іваненко", "contribution_percent": 100}]
  }'
```

---

## Функціональність

- **Завантаження файлів** — підтримка .docx, .pdf, .txt
- **NLP-обробка** — автоматичне виявлення термінів (KeyBERT), розрахунок частот
- **Переклад** — автоматичний переклад на англійську (deep-translator)
- **Wizard** — 3-крокова форма: файл → перегляд термінів/технологій → автори/домен
- **Список документів** — фільтрація, сортування, видалення
- **Спеціалісти** — автоматично формуються на основі авторів документів
- **Словники** — автоматично формуються на основі термінів у межах домену
- **Обробка помилок** — глобальний ErrorBoundary + Toast-сповіщення
