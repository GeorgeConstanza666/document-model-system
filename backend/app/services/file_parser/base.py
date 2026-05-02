from abc import ABC, abstractmethod


class FileParser(ABC):
    """Abstract base for all file-text extractors."""

    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """Return the full plain-text content of the file at *file_path*."""
