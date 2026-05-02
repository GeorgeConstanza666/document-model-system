# Програмна система для створення документної моделі організації проєкту

Дипломний проєкт. Реалізація модуля документів на основі статті Кунгурцева та Чорби (2025):
"Терм-словникова технологія відбору виконавців задач у проєктах розробки програмного забезпечення".

## Модель документа

```
Doc = ⟨idD, sAuthor, SubjArea, Date, sDocTerm, sTechnology⟩
```

| Поле | Опис |
|------|------|
| `idD` | Ідентифікатор документа |
| `sAuthor` | Множина авторів із внесками (сума = 100%) |
| `SubjArea` | Предметна область |
| `Date` | Дата створення |
| `sDocTerm` | Терміни з частотою |
| `sTechnology` | Технології зі ступенем використання |

## Стек технологій

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, SQLite, Pydantic
- **NLP:** KeyBERT, spaCy, deep-translator, langdetect
- **Парсинг файлів:** python-docx, pdfplumber
- **Frontend:** React 18, Vite, TailwindCSS, React Query, axios

## Структура проєкту

```
document-model-system/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # HTTP роутери
│   │   ├── core/             # Конфігурація, база даних
│   │   ├── models/           # SQLAlchemy моделі
│   │   ├── schemas/          # Pydantic схеми
│   │   ├── services/         # Бізнес-логіка
│   │   │   ├── nlp/
│   │   │   ├── translation/
│   │   │   └── file_parser/
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│   └── package.json
├── .gitignore
├── README.md
└── CLAUDE.md
```

## Встановлення та запуск

### Backend

```bash
cd backend

# Створити та активувати віртуальне середовище
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

# Встановити залежності
pip install -r requirements.txt

# Скопіювати конфігурацію
copy .env.example .env

# Запустити сервер розробки
uvicorn app.main:app --reload
```

Сервер буде доступний за адресою: http://localhost:8000

Документація API: http://localhost:8000/docs

### Frontend

```bash
cd frontend

# Встановити залежності
npm install

# Запустити сервер розробки
npm run dev
```

Фронтенд буде доступний за адресою: http://localhost:5173

### Тести

```bash
cd backend
pytest
```
