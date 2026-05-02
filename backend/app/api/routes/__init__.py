from app.api.routes.authors import router as authors_router
from app.api.routes.dictionaries import router as dictionaries_router
from app.api.routes.documents import router as documents_router
from app.api.routes.domains import router as domains_router
from app.api.routes.specialists import router as specialists_router

__all__ = [
    "authors_router",
    "dictionaries_router",
    "documents_router",
    "domains_router",
    "specialists_router",
]
