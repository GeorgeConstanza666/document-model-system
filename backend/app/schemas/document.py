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
