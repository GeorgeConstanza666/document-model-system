"""
Seed the database with 5 example documents across different domains.

Usage (from the backend/ directory):
    python scripts/seed.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date

from app.core.database import SessionLocal, engine
from app.models import Base
from app.models.author import Author, Specialist
from app.models.document import AuthorContribution, Document, DocumentTechnology, DocumentTerm
from app.models.domain import Dictionary, DictionaryEntry, Domain
from app.models.technology import Technology
from app.models.term import Term

SEED_DATA = [
    {
        "domain": "Машинне навчання",
        "file_name": "image_recognition_system.docx",
        "date": date(2024, 3, 15),
        "original_text": (
            "Система розпізнавання зображень побудована на основі згорткових нейронних мереж. "
            "Використовуються техніки глибокого навчання для класифікації об'єктів. "
            "Модель навчена на наборі даних ImageNet із точністю 94%."
        ),
        "translated_text": (
            "The image recognition system is built on convolutional neural networks. "
            "Deep learning techniques are used for object classification. "
            "The model is trained on the ImageNet dataset with 94% accuracy."
        ),
        "source_language": "uk",
        "authors": [
            {"full_name": "Іван Коваленко", "email": "kovalenko@example.com", "contribution_percent": 60.0},
            {"full_name": "Олена Петренко", "email": "petrenko@example.com", "contribution_percent": 40.0},
        ],
        "terms": [
            {"term": "image recognition", "q_term": 3, "rel_freq_term": 6.5217},
            {"term": "deep learning", "q_term": 2, "rel_freq_term": 4.3478},
            {"term": "convolutional neural network", "q_term": 1, "rel_freq_term": 2.1739},
            {"term": "object classification", "q_term": 1, "rel_freq_term": 2.1739},
            {"term": "training dataset", "q_term": 1, "rel_freq_term": 2.1739},
        ],
        "technologies": [
            {"name": "Python", "degree_of_use": 30.0},
            {"name": "TensorFlow", "degree_of_use": 20.0},
            {"name": "NumPy", "degree_of_use": 10.0},
        ],
    },
    {
        "domain": "Веб-розробка",
        "file_name": "ecommerce_rest_api.pdf",
        "date": date(2024, 5, 22),
        "original_text": (
            "Розроблено REST API для e-commerce платформи з авторизацією через JWT. "
            "Реалізовано ендпоінти для керування товарами, замовленнями та користувачами. "
            "PostgreSQL використовується як основна база даних."
        ),
        "translated_text": (
            "A REST API has been developed for an e-commerce platform with JWT authorization. "
            "Endpoints for managing products, orders, and users have been implemented. "
            "PostgreSQL is used as the primary database."
        ),
        "source_language": "uk",
        "authors": [
            {"full_name": "Максим Шевченко", "email": "shevchenko@example.com", "contribution_percent": 100.0},
        ],
        "terms": [
            {"term": "rest api", "q_term": 2, "rel_freq_term": 5.2632},
            {"term": "jwt authorization", "q_term": 1, "rel_freq_term": 2.6316},
            {"term": "endpoint design", "q_term": 1, "rel_freq_term": 2.6316},
            {"term": "database management", "q_term": 1, "rel_freq_term": 2.6316},
        ],
        "technologies": [
            {"name": "Node.js", "degree_of_use": 30.0},
            {"name": "PostgreSQL", "degree_of_use": 20.0},
            {"name": "Docker", "degree_of_use": 10.0},
        ],
    },
    {
        "domain": "DevOps",
        "file_name": "cicd_pipeline_automation.txt",
        "date": date(2024, 7, 10),
        "original_text": (
            "Автоматизовано CI/CD pipeline за допомогою GitHub Actions та Docker. "
            "Kubernetes використовується для оркестрації контейнерів у продакшн-середовищі. "
            "Моніторинг системи здійснюється через Prometheus та Grafana."
        ),
        "translated_text": (
            "The CI/CD pipeline has been automated using GitHub Actions and Docker. "
            "Kubernetes is used for container orchestration in the production environment. "
            "System monitoring is performed through Prometheus and Grafana."
        ),
        "source_language": "uk",
        "authors": [
            {"full_name": "Андрій Бойко", "email": "boyko@example.com", "contribution_percent": 50.0},
            {"full_name": "Тетяна Мороз", "email": "moroz@example.com", "contribution_percent": 50.0},
        ],
        "terms": [
            {"term": "continuous integration", "q_term": 2, "rel_freq_term": 4.7619},
            {"term": "container orchestration", "q_term": 1, "rel_freq_term": 2.3810},
            {"term": "deployment pipeline", "q_term": 1, "rel_freq_term": 2.3810},
            {"term": "system monitoring", "q_term": 1, "rel_freq_term": 2.3810},
        ],
        "technologies": [
            {"name": "Docker", "degree_of_use": 30.0},
            {"name": "Kubernetes", "degree_of_use": 20.0},
            {"name": "GitHub Actions", "degree_of_use": 20.0},
            {"name": "AWS", "degree_of_use": 10.0},
        ],
    },
    {
        "domain": "Кібербезпека",
        "file_name": "web_security_analysis.docx",
        "date": date(2024, 9, 5),
        "original_text": (
            "Проведено аналіз захищеності веб-додатку методами пентестингу. "
            "Виявлено вразливості типу SQL injection та XSS. "
            "Розроблено рекомендації щодо шифрування даних та захисту від атак."
        ),
        "translated_text": (
            "A web application security analysis has been conducted using penetration testing methods. "
            "Vulnerabilities of SQL injection and XSS types have been identified. "
            "Recommendations on data encryption and attack prevention have been developed."
        ),
        "source_language": "uk",
        "authors": [
            {"full_name": "Сергій Лисенко", "email": "lysenko@example.com", "contribution_percent": 70.0},
            {"full_name": "Марина Іваненко", "email": "ivanenko@example.com", "contribution_percent": 30.0},
        ],
        "terms": [
            {"term": "penetration testing", "q_term": 2, "rel_freq_term": 5.0},
            {"term": "sql injection", "q_term": 1, "rel_freq_term": 2.5},
            {"term": "data encryption", "q_term": 1, "rel_freq_term": 2.5},
            {"term": "security vulnerability", "q_term": 1, "rel_freq_term": 2.5},
            {"term": "xss attack", "q_term": 1, "rel_freq_term": 2.5},
        ],
        "technologies": [
            {"name": "Python", "degree_of_use": 20.0},
            {"name": "Linux", "degree_of_use": 10.0},
        ],
    },
    {
        "domain": "Мобільна розробка",
        "file_name": "elearning_mobile_app.pdf",
        "date": date(2024, 11, 18),
        "original_text": (
            "Розроблено мобільний додаток для навчання з підтримкою офлайн-режиму. "
            "Push-сповіщення реалізовані через Firebase Cloud Messaging. "
            "Інтерфейс побудований на React Native для кросплатформної підтримки."
        ),
        "translated_text": (
            "A mobile learning application has been developed with offline mode support. "
            "Push notifications are implemented via Firebase Cloud Messaging. "
            "The interface is built on React Native for cross-platform support."
        ),
        "source_language": "uk",
        "authors": [
            {"full_name": "Дмитро Олійник", "email": "oliynyk@example.com", "contribution_percent": 100.0},
        ],
        "terms": [
            {"term": "mobile application", "q_term": 2, "rel_freq_term": 5.8824},
            {"term": "offline mode", "q_term": 1, "rel_freq_term": 2.9412},
            {"term": "push notification", "q_term": 1, "rel_freq_term": 2.9412},
            {"term": "cross platform", "q_term": 1, "rel_freq_term": 2.9412},
            {"term": "user interface", "q_term": 1, "rel_freq_term": 2.9412},
        ],
        "technologies": [
            {"name": "React", "degree_of_use": 30.0},
            {"name": "JavaScript", "degree_of_use": 20.0},
            {"name": "Firebase", "degree_of_use": 10.0},
        ],
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.query(Document).count() > 0:
            print("База даних вже містить документи. Seed пропущено.")
            return

        print("Заповнення бази даних тестовими даними...")

        for entry in SEED_DATA:
            # Domain
            domain = db.query(Domain).filter(Domain.name == entry["domain"]).first()
            if domain is None:
                domain = Domain(name=entry["domain"])
                db.add(domain)
                db.flush()

            # Document
            doc = Document(
                subj_area_id=domain.id,
                date=entry["date"],
                file_name=entry["file_name"],
                original_text=entry["original_text"],
                translated_text=entry["translated_text"],
                source_language=entry["source_language"],
            )
            db.add(doc)
            db.flush()

            # Authors + Specialists
            author_ids = []
            for a_data in entry["authors"]:
                author = db.query(Author).filter(Author.full_name == a_data["full_name"]).first()
                if author is None:
                    author = Author(full_name=a_data["full_name"], email=a_data["email"])
                    db.add(author)
                    db.flush()
                author_ids.append(author.id)
                db.add(AuthorContribution(
                    document_id=doc.id,
                    author_id=author.id,
                    contribution_percent=a_data["contribution_percent"],
                ))

            # Terms
            term_ids = []
            for t_data in entry["terms"]:
                term = db.query(Term).filter(Term.text_en == t_data["term"]).first()
                if term is None:
                    term = Term(text_en=t_data["term"])
                    db.add(term)
                    db.flush()
                term_ids.append(term.id)
                db.add(DocumentTerm(
                    document_id=doc.id,
                    term_id=term.id,
                    q_term=t_data["q_term"],
                    rel_freq_term=t_data["rel_freq_term"],
                ))

            # Technologies
            for tech_data in entry["technologies"]:
                tech = db.query(Technology).filter(Technology.name == tech_data["name"]).first()
                if tech is None:
                    tech = Technology(name=tech_data["name"])
                    db.add(tech)
                    db.flush()
                db.add(DocumentTechnology(
                    document_id=doc.id,
                    technology_id=tech.id,
                    degree_of_use=tech_data["degree_of_use"],
                ))

            # Specialists
            for author_id in author_ids:
                if not db.query(Specialist).filter(Specialist.author_id == author_id).first():
                    db.add(Specialist(author_id=author_id))

            # Dictionary
            dictionary = db.query(Dictionary).filter(Dictionary.domain_id == domain.id).first()
            if dictionary is None:
                dictionary = Dictionary(domain_id=domain.id)
                db.add(dictionary)
                db.flush()

            # Dictionary entries
            for term_id in term_ids:
                if not db.query(DictionaryEntry).filter(
                    DictionaryEntry.dictionary_id == dictionary.id,
                    DictionaryEntry.term_id == term_id,
                ).first():
                    db.add(DictionaryEntry(dictionary_id=dictionary.id, term_id=term_id))

            print(f"  ✓ {entry['file_name']} [{entry['domain']}]")

        db.commit()
        print(f"\nГотово! Додано {len(SEED_DATA)} документів.")

    except Exception as exc:
        db.rollback()
        print(f"Помилка: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
