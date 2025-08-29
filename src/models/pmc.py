from pydantic import BaseModel, Field
from typing import List, Optional

class PmcAuthor(BaseModel):
    name: str

class PmcArticle(BaseModel):
    pmcid: str
    title: str
    abstract: Optional[str] = None
    authors: List[PmcAuthor] = Field(default_factory=list)
    journal: Optional[str] = None
    publication_year: Optional[int] = None
    full_text: Optional[str] = None
