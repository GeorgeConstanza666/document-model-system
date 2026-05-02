# Project context

## Goal
Implement the Document module from the paper "A term-dictionary-based technology for selecting task executors in software development projects" by Kungurtsev & Chorba (2025).

This is a thesis project for a software engineering student.
Topic: "Software system for creating a document model of a project organization".

## Document model (paper, formula 3)
Doc = ⟨idD, sAuthor, SubjArea, Date, sDocTerm, sTechnology⟩

Where:
- idD: document identifier
- sAuthor: set of authors with contributions (sum = 100%)
- SubjArea: subject area / domain
- Date: creation date
- sDocTerm: set of terms with qTerm (count) and relFreqTerm (relative frequency, %)
- sTechnology: set of technologies with degreeOfUseTech

Sub-models:
- DocTerm = ⟨Term, qTerm, relFreqTerm⟩
- Technology = ⟨nameTech, degreeOfUseTech⟩
- Author = ⟨idAuthor, authorContrib⟩

## Tech stack
- Backend: FastAPI, SQLAlchemy, SQLite, Pydantic, Python 3.11+
- NLP: KeyBERT, spaCy, deep-translator, langdetect
- File parsing: python-docx, pdfplumber
- Frontend: React 18, Vite, TailwindCSS, React Query, axios, React Router

## Project structure
```
document-model-system/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   ├── core/          (config, database)
│   │   ├── models/        (SQLAlchemy)
│   │   ├── schemas/       (Pydantic)
│   │   ├── services/      (business logic)
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
├── README.md
└── CLAUDE.md
```

## Code style
- Code, variable names, comments: English
- UI text (labels, buttons, messages, errors shown to user): Ukrainian
- Use Python type hints
- Use functional React components with hooks
- Document classes/functions with docstrings
- Format Python with black, lint with ruff

## Out of scope
- Do NOT implement Task module logic
- Specialist module: minimal — just link authors to their documents
- Vocab module: minimal — store dictionary entries linked to terms
- No authentication (single-user thesis project)
- No deployment / cloud

## Important rules
- Never write code outside the requested step
- Always show terminal commands the user needs to run
- After each step, list what was created and how to verify it