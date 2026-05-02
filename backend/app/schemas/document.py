from pydantic import BaseModel, Field


class DocTermDraft(BaseModel):
    """NLP-extracted term with frequency statistics — DocTerm = ⟨Term, qTerm, relFreqTerm⟩."""

    term: str
    q_term: int = Field(ge=0, description="Absolute occurrence count in the source text")
    rel_freq_term: float = Field(ge=0.0, description="Relative frequency as % of total words")


class TechnologyDraft(BaseModel):
    """Technology name with degree of use — Technology = ⟨nameTech, degreeOfUseTech⟩."""

    name: str
    degree_of_use: float = Field(ge=0.0, le=100.0, description="Degree of use, 0–100 %")


class ProcessedDocumentDraft(BaseModel):
    """Full result of the document processing pipeline — ready for DB persistence."""

    file_name: str
    original_text: str
    translated_text: str
    source_language: str
    extracted_terms: list[DocTermDraft]
    extracted_technologies: list[TechnologyDraft]
